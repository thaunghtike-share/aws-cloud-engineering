## configure aws

### 1. Configure AWS CLI

```bash
aws configure
```

Enter these values:

```text
AWS Access Key ID
AWS Secret Access Key
Default region name
Default output format
```

Example region:

```text
ap-southeast-1
```

Example output format:

```text
json
```

### 2. Check Current AWS Account

```bash
aws sts get-caller-identity
```

### 3. List IAM Users

```bash
aws iam list-users
```

### 4. Get Current IAM User

```bash
aws iam get-user
```

### 5. Check User Attached Policies

```bash
aws iam list-attached-user-policies --user-name t.htike.oo
```

### 6. Create IAM user

```bash
aws iam create-user --user-name developer
```

### 7. Verify user created

```bash
aws iam list-users
```

### 8. Attach AdministratorAccess Policy

```bash
aws iam attach-user-policy \
  --user-name developer \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
```

### 9. Verify Attached Policies

```bash
aws iam list-attached-user-policies --user-name developer
```

