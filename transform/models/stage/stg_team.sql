with source as (
  
	SELECT 
    	team.myteamid,
    	(portals.value::json->>'type')::bigint as type,
    	(portals.value::json->>'zsoid')::varchar zsoid,
		(portals.value::json->>'tapzoho')::varchar tapzoho,
		(portals.value::json->>'isshowteam')::varchar isshowteam,
		(portals.value::json->>'portalOwner')::varchar portalOwner,
		(ownertreamids.value::json->>0)::int ownerteamids
	FROM  {{ source('tap_zohosprints', 'team') }}, 
		lateral jsonb_array_elements(tap_zohosprints.team.portals) portals,
    	lateral jsonb_array_elements(tap_zohosprints.team.ownerteamids) ownertreamids

)

select * from source
