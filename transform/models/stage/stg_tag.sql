with source as (
  
    SELECT 
        tagid::varchar tag_id,
        itemtagcount::bigint item_tag_count,
        hasitemtagpermission::bool has_item_tag_permission,
        myteamid::bigint my_team_id,
        next::bool has_next,
        status::varchar status,
        userdisplayname::jsonb user_display_name,
        (tag.record->>'tagName')::varchar tag_name,
        (tag.record->>'colorCode')::varchar color_code,
        (tag.record->>'createdBy')::varchar created_by
    FROM {{ source('tap_zohosprints', 'tag') }}
)

select * from source
