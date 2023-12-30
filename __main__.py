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
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDhBb6oZrgpGyCd1Kb3d3fSNhbdxqxeVmZxR6RvMZmUS2nUC4U5XI1IRno+lY8jYVrU5CYQRi5cMDjWlQH0Qgh/T/siCEt8giaOB0VXOBaWaj4sqQglLCPwebhWbw5AHMqgk2wrxe+Soxmsj5I55KNkpdNnDog/R2pLFD1a5r99FCzJbUeDebWtWFPq0wwGtQUu2Gpg6iMiUCNdhaWXWOQ0fFnvZeQ/xiA8zoFlUZWgbbSP+BbKVXgi+TZk89qtYp+DGMbx5uoNhAyjBkIRlOvzfqVlNTH8CRETa8mPU6DbF1uTLJ46ZhdNpv8Po/ONUgPiQjlequnn1LYm8UjhDWuLszlIGUN8bXwUUj0+kT6UYGg7qeTycfbFRp2ndtRdgL4v9/2VgTkveti6GBbOxtdDSHFFdIVO+befk+uhOyOgNnH4b2u4JSa/F0Mo4LXf001GHvON5kYHcHVRv76q9MLs4QbhLzVXIPUdwQAyo3Nk9qWQ4WKr0SlD6s0609iVX3CvwsjkuyEXCVwvKDULqLTZ9azDvhGYvxnB+9Gyo4qIDh/Znu1V0q3YudO2pkzo/EEQzJsw8T28I9cnTAeSOR+jo+poGg2ZaOyFBLUASqNpS8Xj+fBLDMG1VCK5lZXYEHlBYMs2YNWTHDGLJxtXxZPJfUmccQpIIgCZVpUsTAu3bw== nabil@zenbook",
)

# file_to_upload = s3.BucketObject(
#     "my-home-page", bucket=bucket.bucket, source=pulumi.FileAsset("./site/index.html")
# )

# CONFIGURATIONS AND SECRETS
config = pulumi.Config()

# EC2 SECURITY GROUPS
ec2_security_group = ec2.SecurityGroup(
    "webserver-security-group", description="security group for webservers"
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
)


# RDS SECURITY GROUP
rds_security_group = ec2.SecurityGroup(
    "rds-security-group",
    description="security group for rds instance",
)

# TODO: HOW THE TF DO YOU CONNECT ECS TO RDS? 🤬
# # RDS SECURITY GROUP RULES
# rds_ingress_rule = ec2.SecurityGroupRule(
#     "RdsTraffic",
#     type="ingress",
#     from_port=5432,
#     to_port=5432,
#     protocol="tcp",
#     security_group_id=rds_security_group.id,
#     source_security_group_id=ec2_security_group.id,
# )

# RDS: POSTGRESQL
postgresql = rds.Instance(
    "postgres-db",
    apply_immediately=True,
    allocated_storage=20,
    engine="postgres",
    engine_version="15",
    instance_class="db.t3.micro",
    vpc_security_group_ids=[ec2_security_group.id],
    db_name="postgres",
    username="postgres",
    password=config.require_secret("database_password"),
    skip_final_snapshot=True,
    publicly_accessible=False,
)

pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("instance_url", ec2_instance.public_dns)
pulumi.export("db_address", postgresql.address)
pulumi.export("db_endpoint", postgresql.endpoint)
pulumi.export("db_name", postgresql.db_name)
