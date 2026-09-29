# QMS Training

## Purpose
QMS Training manages training assignments, validity, qualification evidence and employee competency requirements connected to the management system.

## Main capabilities
- Create training courses with validity duration.
- Categorize courses as induction, procedure, quality, safety, compliance, technical or other.
- Link training courses to QMS requirements.
- Link training courses to controlled documents.
- Assign courses to employees/users.
- Set due dates and minimum scores.
- Record completion date and completion score.
- Calculate training expiry dates from course validity.
- Attach evidence to completed training.
- Automatically mark expired completed training as expired.
- Define competency requirements by role/function.
- Define expected competency level from awareness to expert.
- Link competencies to processes and required courses.
- Record employee competency assessments and evidence.
- Track qualified, provisional, expired and not-met competency status.

## Models
- `qms.training.course`
- `qms.training.assignment`
- `qms.competency.requirement`
- `qms.employee.competency`

## Training workflow
`Assigned → Completed → Expired` or `Cancelled`

Completion validates the score against the minimum required score and calculates the expiry date.

## Competency levels
`Awareness / Basic / Working / Advanced / Expert`

## Menu
- QMS / People / Training Courses
- QMS / People / Training Assignments
- QMS / People / Competency Requirements
- QMS / People / Employee Competencies

## Dependencies
`qms_core`, `qms_documents`, `mail`.
