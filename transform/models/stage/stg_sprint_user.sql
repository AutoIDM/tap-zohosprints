with source as (
    SELECT
        userid::varchar user_id,
        myteamid::varchar my_team_id,
        next::bool has_next,
        projectid::varchar project_id,
        sprintid::varchar sprint_id,
        status::varchar status,
        (sprint_user.record->>'roleId')::varchar role_id,
        (sprint_user.record->>'emailId')::varchar email_id,
        (sprint_user.record->>'addedVia')::bigint added_via,
        (sprint_user.record->>'integObj')::jsonb integObj,
        (sprint_user.record->>'userType')::bigint user_type,
        (sprint_user.record->>'companyId')::varchar company_id,
        (sprint_user.record->>'iamUserId')::varchar i_am_user_id,
        (sprint_user.record->>'userStatus')::bigint user_status,
        (sprint_user.record->>'displayName')::varchar display_name,
        (sprint_user.record->>'isConfirmed')::bool is_confirmed,
        (sprint_user.record->>'licenseType')::bigint license_type,
        (sprint_user.record->>'hasPerm_viewuserdet')::bool has_perm_viewuserdet,
        (sprint_user.record->>'integrationUserType')::bigint integration_user_type  
    FROM {{ source('tap_zohosprints', 'sprint_user') }}
)

select * from source
