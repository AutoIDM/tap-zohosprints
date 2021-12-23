with source as (
    SELECT
epicid::varchar epic_id,
myteamid::varchar my_team_id,
projectid::varchar project_id,
(epic.record->>'owner')::varchar owner_id,
(epic.record->>'epicNo')::varchar epic_number,
(epic.record->>'epicName')::varchar epic_name,
(epic.record->>'epicType')::varchar epic_type,
(epic.record->>'sequence')::bigint sequence,
(epic.record->>'colorCode')::varchar color_code,
(epic.record->>'createdBy')::varchar created_by_id,
(epic.record->>'epicStatus')::bigint epic_status,
(epic.record->>'createdTime')::varchar created_time,
userdisplayname::jsonb userdisplayname ,
zsuseridvszuid::jsonb zsuseridvszuid
    FROM {{ source('tap_zohosprints', 'epic') }}

)

select * from source
