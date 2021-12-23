with source as (
    SELECT
    sprintid::varchar sprint_id,
    myteamid::varchar my_team_id,
    projectid::varchar project_id,
    (sprint.record->>'endDate')::varchar end_date,
    (sprint.record->>'duration')::varchar duration,
    (sprint.record->>'sprintNo')::varchar sprint_number,
    (sprint.record->>'createdBy')::varchar created_by,
    (sprint.record->>'startDate')::varchar start_date,
    (sprint.record->>'canceledBy')::varchar canceled_by,
    (sprint.record->>'canceledOn')::varchar canceled_on,
    (sprint.record->>'sprintName')::varchar sprint_name,
    (sprint.record->>'sprintType')::bigint sprint_type,
    (sprint.record->>'startAfter')::varchar start_after,
    (sprint.record->>'workflowId')::varchar workflow_id,
    (sprint.record->>'completedOn')::varchar completed_on,
    (sprint.record->>'createdTime')::date created_time,
    (sprint.record->>'scrumMaster')::varchar scrum_master,
    userdisplayname::jsonb userdisplayname,
    zsuseridvszuid ::jsonb zsuseridvszuid    
    FROM {{ source('tap_zohosprints', 'sprint') }}

)

select * from source
