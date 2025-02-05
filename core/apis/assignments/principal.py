from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment

from .schema import AssignmentSchema, AssignmentGradeSchema
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)


@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    '''Returns list of assignments'''
    principals_assignments = Assignment.get_assignments_by_principal()
    principals_assignments_dump = AssignmentSchema().dump(principals_assignments, many=True)
    return APIResponse.respond(data=principals_assignments_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
        # Grade an assignment
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    try:
        graded_assignment = Assignment.mark_grade(
            _id=grade_assignment_payload.id,
            grade=grade_assignment_payload.grade,
            auth_principal=p
        )
        db.session.commit()
        graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
        return APIResponse.respond(data=graded_assignment_dump)
    
    except AssertionError as e:
        #  Ensure that validation errors are correctly returned as 400
        return APIResponse.respond_error(str(e), 400)


from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse

# Import the custom error class for consistent error responses
from core.libs.exceptions import FyleError

from core.models.assignments import (
    Assignment,
    AssignmentStateEnum,
    GradeEnum
)
from .schema import AssignmentSchema, AssignmentGradeSchema

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    '''
    Returns list of assignments that the principal can view.
    '''
    principals_assignments = Assignment.get_assignments_by_principal()
    principals_assignments_dump = AssignmentSchema().dump(principals_assignments, many=True)
    return APIResponse.respond(data=principals_assignments_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    '''
    Grade an assignment (or re-grade if already graded).
    The tests require:
    - 400 if the assignment is in DRAFT state.
    - 404 if the assignment doesn't exist.
    - Validate the incoming grade is part of GradeEnum.
    '''
    # Parse incoming JSON payload
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    assignment_id = grade_assignment_payload.id
    new_grade = grade_assignment_payload.grade

    # Fetch the assignment
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if not assignment:
        raise FyleError("Assignment not found", 404)

    #  Prevent grading of DRAFT assignments
    if assignment.state == AssignmentStateEnum.DRAFT:
        raise FyleError("Cannot grade a draft assignment", 400)

    #  Ensure grade is valid
    if new_grade not in [g.value for g in GradeEnum]:
        raise FyleError(f"Invalid grade '{new_grade}'", 400)

    try:
        #  Update the assignment state and grade
        assignment.grade = new_grade
        assignment.state = AssignmentStateEnum.GRADED
        db.session.commit()

        #  Return the updated assignment
        graded_assignment_dump = AssignmentSchema().dump(assignment)
        return APIResponse.respond(data=graded_assignment_dump)

    except Exception as e:
        db.session.rollback()
        return APIResponse.respond_error(str(e), 500)  # Ensure server errors are handled
"""
from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.libs.exceptions import FyleError
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
from .schema import AssignmentSchema, AssignmentGradeSchema

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    principals_assignments = Assignment.filter(Assignment.state != AssignmentStateEnum.DRAFT).all()
    principals_assignments_dump = AssignmentSchema().dump(principals_assignments, many=True)
    return APIResponse.respond(data=principals_assignments_dump)

@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    try:
        graded_assignment = Assignment.mark_grade(
            _id=incoming_payload['id'],
            grade=incoming_payload['grade'],
            auth_principal=p
        )
        db.session.commit()

        graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
        return APIResponse.respond(data=graded_assignment_dump)

    except FyleError as e:
        db.session.rollback()
        return APIResponse.respond_error(str(e), e.code)

    except Exception as e:
        db.session.rollback()
        return APIResponse.respond_error(str(e), 500)
"""