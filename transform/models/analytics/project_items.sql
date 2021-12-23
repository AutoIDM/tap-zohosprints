with items as (
    
    select * from {{ ref('items') }}

), project as (
    
    select * from {{ ref('stg_project') }}

), final as (

    select project.project_name, count(*)
    from items
    left join project on project.project_id = items.project_id
    group by project_name

)
select * from final
