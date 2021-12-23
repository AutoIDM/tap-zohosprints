with source as (
  SELECT
         team.myteamid::varchar team_id,
         team.portals::jsonb portals,
         team.ownerteamids::jsonb owner_team_ids
	FROM  {{ source('tap_zohosprints', 'team') }}

)

select * from source
