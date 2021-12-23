with sprints as (
    
    select * from {{ ref('stg_item_details_backlog') }}

), backlog_items as (

    select * from {{ ref('stg_item_details_sprint') }}

), final as (

select * from sprints
union all
select * from backlog_items

)
select * from final
