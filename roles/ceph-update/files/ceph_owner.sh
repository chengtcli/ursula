# it's faster to use uid/gid than username/groupname
uid=$(id -u ceph)
gid=$(id -g ceph)

chown $uid:$gid /var/lib/ceph

# chown for all dirs under /var/lib/ceph except /var/lib/ceph/osd
for ceph_sub in $(find /var/lib/ceph/ -maxdepth 1 -mindepth 1 |grep -v "var/lib/ceph/osd")
do
	chown -R $uid:$gid $ceph_sub
done

# deal with osd dir
chown $uid:$gid /var/lib/ceph/osd
for osd in $(find /var/lib/ceph/osd -maxdepth 1 -mindepth 1)
do
	chown $uid:$gid $osd
	chown $uid:$gid $osd/current
	# run this in parallel, because it's time consuming
	for pg in $(find $osd/current -maxdepth 1 -mindepth 1)
	do
		chown -R $uid:$gid $pg &
	done
	for osd_sub in $(find $osd -maxdepth 1 -mindepth 1 |grep -v "current")
	do
		chown -R $uid:$gid $osd_sub
	done
done
wait
