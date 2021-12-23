with source as (
SELECT
itemid::varchar item_id,
backlogid::varchar backlog_id,
myteamid::varchar my_team_id,
projectid::varchar project_id,
sprintid::varchar sprint_id,
integobj::jsonb integobj,
(item_details_backlog.record->>'depth')::varchar depth,
(item_details_backlog.record->>'epicId')::varchar epic_id,
(item_details_backlog.record->>'itemNo')::varchar item_number,
(item_details_backlog.record->>'points')::bigint points,
(item_details_backlog.record->>'endDate')::varchar end_date,
(item_details_backlog.record->>'ownerId')::jsonb owner_ids,
(item_details_backlog.record->>'addedVia')::bigint added_via,
(item_details_backlog.record->>'duration')::varchar duration,
(item_details_backlog.record->>'isParent')::bool is_parent,
(item_details_backlog.record->>'itemName')::varchar item_name,
(item_details_backlog.record->>'rootItem')::varchar root_item,
(item_details_backlog.record->>'sequence')::varchar sequence,
(item_details_backlog.record->>'statusId')::varchar status_id,
(item_details_backlog.record->>'tagCount')::bigint tag_count,
(item_details_backlog.record->>'UDF_CHAR3')::varchar udf_char3, --user defined field, should match this to name whatever the field is (maybe we can make this dynamic?)
(item_details_backlog.record->>'createdBy')::varchar created_by_id,
(item_details_backlog.record->>'startDate')::varchar start_date,
(item_details_backlog.record->>'parentItem')::varchar parent_item,
(item_details_backlog.record->>'startAfter')::varchar start_after,
(item_details_backlog.record->>'completedBy')::varchar completed_by,
(item_details_backlog.record->>'createdTime')::varchar created_time,
(item_details_backlog.record->>'description')::varchar description,
(item_details_backlog.record->>'isDocsAdded')::bool is_docs_added,
(item_details_backlog.record->>'hasCheckList')::bool has_check_list,
(item_details_backlog.record->>'isIntegrated')::varchar is_integrated,
(item_details_backlog.record->>'isNotesAdded')::bool is_notes_added,
(item_details_backlog.record->>'leftPosition')::bigint left_position,
(item_details_backlog.record->>'releaseCount')::bigint release_count,
(item_details_backlog.record->>'completedDate')::varchar completed_date,
(item_details_backlog.record->>'rightPosition')::varchar right_position,
(item_details_backlog.record->>'projItemTypeId')::varchar project_item_type_id,
(item_details_backlog.record->>'projPriorityId')::varchar project_priority_id,
userdisplayname::jsonb user_display_name,
zsuseridvszuid::jsonb zsuseridvszuid

FROM {{ source('tap_zohosprints', 'item_details_backlog') }}

)

select * from source
