"""An AWS Python Pulumi program"""
import pulumi
from pulumi_aws import ec2, rds

# # Create an AWS resource (S3 Bucket)
# bucket = s3.Bucket("my-bucket")

# # Export the name of the bucket
# pulumi.export("bucket_name", bucket.id)

# PUBLIC KEY
aws_public_key = ec2.KeyPair(
    "aws_public_key",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC1ebFXHmz3ry8khsnQeGVINKg/VMaXdsbQF0mcUq8VQSFSbAYJhu1tues9ECVLjEWAJbdHQDtYwk2iKId369UN+XY0Rmljk5ynB7oFgXmKzs6a1kE1q3av6Zcg+A3UbSUoDyld4YxP0BHM+4tHnNWGHooqGYNOzcnW83AqKR0uV0ul1G8dklFtOXpPQ/Qb7IjVI9APKREuMlVIXmUAGUBA5cR+TzUk7MCFBUMvac23cRfiiUOSPJzmQi57XSVlbGaw83b4jZXIkt2Tx/JJuMsgh7JCfXBTuhilVEJcgNTV7SkP2d2k8IROHnr8NloKd89qWCRQJmqqo/SqbX3071vIIB/p/l1UCEkCtLF9wYQr3lh9p1Qen8+M8/bEGFA/oGXpJyG79kZ7yCCqTXfvNq2zXwtXgOHzRHCpfpb+l0a696Vc8WwMwX3ctWLrEeb3/p2xOap6UE5UPfL9XCGDxjw3darIrYovLwdPiQ34s2rzJshqKKXktDk/aW21PLVqi4aefu4hU9LxiDw2wk7izFzYFp/TtbAzNMKFmf0ttWUxFrxIRA3wU1rmD204AHa4SBV5S7ZQzwKzbnoBPvkzl/LdsaOAmUxWLWkoFStw3UGcGQbU33biab6oIPYsHxCPLYK5AceTzP5DSeFAMBRJIRowNhl/rDA5rCNG3vUNR+5qMQ== nabil@zenbook",
)

# file_to_upload = s3.BucketObject(
#     "my-home-page", bucket=bucket.bucket, source=pulumi.FileAsset("./site/index.html")
# )

# CONFIGURATIONS AND SECRETS
config = pulumi.Config()


# SECURITY GROUPS
ec2_security_group = ec2.SecurityGroup(
    "webserver-security-group", description="security group for webservers"
)

rds_security_group = ec2.SecurityGroup(
    "rds-security-group", description="security group for rds instance"
)


# EC2: SECURITY GROUP RULES
allow_ssh = ec2.SecurityGroupRule(
    "AllowSSH",
    type="ingress",
    from_port=22,
    to_port=22,
    protocol="tcp",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=ec2_security_group.id,
)

allow_http = ec2.SecurityGroupRule(
    "AllowHTTP",
    type="ingress",
    from_port=80,
    to_port=80,
    protocol="tcp",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=ec2_security_group.id,
)

allow_all = ec2.SecurityGroupRule(
    "AllowAll",
    type="ingress",
    from_port=0,
    to_port=0,
    protocol="-1",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=ec2_security_group.id,
)

allow_reaching_outside = ec2.SecurityGroupRule(
    "AllowAllOutgoing",
    type="egress",
    from_port=0,
    to_port=0,
    protocol="-1",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=ec2_security_group.id,
)


# EC2 INSTANCES
ec2_instance = ec2.Instance(
    "super-awesome-ec2-instance",
    ami="ami-06dd92ecc74fdfb36",
    instance_type="t2.micro",
    associate_public_ip_address=True,
    key_name=aws_public_key.key_name,
    tags={"Name": "webserver"},
    vpc_security_group_ids=[ec2_security_group.id],
)

# RDS: POSTGRESQL
postgresql = rds.Instance(
    "postgres-db",
    allocated_storage=20,
    engine="postgres",
    engine_version="15",
    instance_class="db.t3.micro",
    vpc_security_group_ids=[ec2_security_group.id],
    db_name="postgres",
    username="postgres",
    password=config.require_secret("database_password"),
)

# RDS: SECURITY GROUPS RULES
allow_traffic_outbound = ec2.SecurityGroupRule(
    "AllowPostgresqlTrafficOut",
    type="egress",
    description="Allows outgoing traffic from the RDS instance",
    protocol="-1",
    from_port=0,
    to_port=0,
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=rds_security_group.id,
)

allow_rds_traffic = ec2.SecurityGroupRule(
    "AllowPostgresqlTraffic",
    type="ingress",
    description="Allows EC2 instance to access into postgresqldb",
    protocol="tcp",
    from_port=5432,
    to_port=5432,
    security_group_id=rds_security_group.id,
    source_security_group_id=ec2_security_group.id,
)

pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("instance_url", ec2_instance.public_dns)
pulumi.export("db_address", postgresql.address)
pulumi.export("db_endpoint", postgresql.endpoint)
pulumi.export("db_name", postgresql.db_name)
