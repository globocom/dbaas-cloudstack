insert into dbaas_cloudstack_databaseinfraoffering (created_at, updated_at, offering_id, databaseinfra_id)
select now(), now(), t4.id, t1.id
from physical_databaseinfra t1
     join dbaas_cloudstack_planattr t2 on (t1.plan_id = t2.plan_id)
     join dbaas_cloudstack_planattr_serviceofferingid t3 on (t2.id = t3.planattr_id)
     join dbaas_cloudstack_cloudstackoffering t4 on (t3.cloudstackoffering_id = t4.id)
where t4.weaker = 0;
