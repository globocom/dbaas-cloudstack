insert into dbaas_cloudstack_cloudstackoffering(created_at,updated_at, serviceofferingid, name, weaker)
select distinct now(), now(), serviceofferingid, 'Service Offering', 0 from dbaas_cloudstack_planattr;

update dbaas_cloudstack_cloudstackoffering
set name = concat(name, ' - ',id);

insert into dbaas_cloudstack_planattr_serviceofferingid(planattr_id, cloudstackoffering_id)
select b.id, a.id
from dbaas_cloudstack_cloudstackoffering a, dbaas_cloudstack_planattr b
where a.serviceofferingid = b.serviceofferingid;


insert into dbaas_cloudstack_cloudstackbundle(created_at,updated_at, zoneid, templateid, networkid, name)
select distinct now(), now(), zoneid, templateid, networkid, 'Bundle' from dbaas_cloudstack_planattr;

update dbaas_cloudstack_cloudstackbundle
set name = concat(name, ' - ',id);

insert into dbaas_cloudstack_planattr_bundle(planattr_id, cloudstackbundle_id)
select b.id, a.id
from   dbaas_cloudstack_cloudstackbundle a , dbaas_cloudstack_planattr b
where  a.zoneid = b.zoneid and a.templateid = b.templateid and a.networkid = b.networkid;

commit;