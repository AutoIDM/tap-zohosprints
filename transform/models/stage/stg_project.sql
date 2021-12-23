with source as (
    SELECT
projectid::varchar project_id,
isstrictscrum::bool is_strict_scrum,
prefix::varchar prefix,
(project.record->>'owner')::varchar owner_id,
(project.record->>'projNo')::varchar project_number,
(project.record->>'status')::varchar status,
(project.record->>'endDate')::varchar end_date,
(project.record->>'groupId')::varchar group_id,
(project.record->>'projName')::varchar project_name,
(project.record->>'projType')::varchar project_type,
(project.record->>'createdBy')::varchar created_by_id,
(project.record->>'integList')::varchar integ_list,
(project.record->>'startDate')::varchar start_date,
(project.record->>'workflowId')::varchar workflow_id,
(project.record->>'createdTime')::varchar createdTime,
(project.record->>'description')::varchar description,
(project.record->>'status_enum')::varchar status_enum,
(project.record->>'projType_enum')::varchar project_type_enum,
(project.record->>'estimationType')::varchar estimation_type,
(project.record->>'estimationType_enum')::varchar estimation_type_enum,
userdisplayname::jsonb userdisplayname,
zsuseridvszuid ::jsonb zsuseridvszuid
    FROM {{ source('tap_zohosprints', 'project') }}

)

select * from source
