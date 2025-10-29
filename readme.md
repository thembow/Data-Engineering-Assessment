## New Math Data Assessment README

### Deployment Instructions
1. Add your AWS account username info to 'vars.tfvars'
If you have been given keys and don't know what your provided username is, you can run
```sh
aws sts get-caller-identity
```
and you should see your username at the end of the Arn
for future, you can save it to an environment variable, 

```sh
export aws_username=$(echo "EnterYourUserNameHere" | tr '[:upper:]' '[:lower:]')
```

2. Initialize your terraform lockfile
```sh
cd terraform/assignment
terraform init 
```
At the time I didn't have bucket access so I figured out you can just do it locally to get around the issue

3. Go into the terraform/assignment and deploy JUST the ecr repo via
```sh
cd ../..
terraform apply -var-file="vars.tfvars" -target="module.ecr_repo"
```
You have to deploy just the ecr repo so u can get the necessary arn to deploy the docker image on

4. Setup the necessary environment variables
```sh
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
export REGION=$(aws configure get region)
export LOCAL_IMAGE_NAME="image_name_example"

export ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
```
5. build docker image, login, tag, and upload
```sh
cd app
docker build -t $LOCAL_IMAGE_NAME .
aws ecr get-login-password | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
docker tag "$LOCAL_IMAGE_NAME" "$ECR_URI"
docker push "$ECR_URI"
```
6. deploy the entire terraform setup
```sh
cd ..
cd terraform/assignment
terraform apply -var-file="vars.tfvars
```

### Testing the setup
1. Upload the sample file, and make sure to substitute <YOUR_PROFILE> for your aws cli profile name
```sh
cd ../..
aws s3 cp sample_orders.csv "s3://nmd-assignment-$aws_username-input-bucket" --profile <YOUR_PROFILE> 
```
2. Wait a minute or so for the lambda to process, then check both your input and output bucket
```sh
aws s3 ls "s3://nmd-assignment-$aws_username-input-bucket" --profile <YOUR_PROFILE>
aws s3 ls "s3://nmd-assignment-$aws_username-output-bucket" --recursive --profile <YOUR_PROFILE>
```
You should see the analytics output files located in analytics/, and log files in logs/

### Analytics Outputs
The analytics folder will contain 3 files..

* most_profitable_region_INPUTFILENAME.csv - the most profitable region and how profitable it was
* number_of_orders_INPUTFILENAME.csv - number of order for each category, and subcategory
* common_ship_method_INPUTFILENAME.csv - most common shipping method for each category; returns first value if there is more than one most frequent value

### Troubleshooting
I ran into some issues early on where I couldn't read the logs, so for sake of seeing where issues appeared I made it so the lambda produces logs for determining where the issue might be cropping up.
1. Look at the files inside the output bucket
```sh
aws s3 ls "s3://nmd-assignment-$aws_username-output-bucket" --recursive --profile <YOUR_PROFILE>
```
2. If you don't see any files inside "/logs", that means that the lambda function wasn't even triggered by your input file upload.
You should see "logs/start_log.txt" at the very least, which indicates the initial code was able to run
3. The "logs/load_log.txt" file has information on if a failure occurred during the input file loading process
4. The "logs/analytics_log.txt" has information on if a failure occurred when creating and outputting the analytics files
This should hopefully be sufficent to determine if the issues start before/during the lambda function
