update dbaas_cloudstack_planattr u
	   join
	   (
		select a.serviceofferingid, b.planattr_id
		from dbaas_cloudstack_cloudstackoffering a , dbaas_cloudstack_planattr_serviceofferingid b
		where a.id = b.cloudstackoffering_id
	   ) x on u.id = x.planattr_id
set u.serviceofferingid = x.serviceofferingid;

update dbaas_cloudstack_planattr u
 	   join
 	   (
		select a.zoneid, a.templateid, a.networkid, b.planattr_id
		from dbaas_cloudstack_cloudstackbundle a , dbaas_cloudstack_planattr_bundle b
		where a.id = b.cloudstackbundle_id
	   ) x on u.id = x.planattr_id
set u.zoneid = x.zoneid,
	u.templateid = x.templateid,
	u.networkid = x.networkid;

commit;
