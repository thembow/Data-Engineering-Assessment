## Update the following terraform code to meet the project requirements
## We have provided some sample code to help you get started

resource "aws_s3_bucket" "input_s3" {
  bucket = lower("${local.app_name}-input-bucket") #bucket name must be all lowercase
  tags = merge({
        Name        = lower("${local.app_name}-input-bucket")
        Environment = "${var.env}"
    }, local.default_tags
  )
  force_destroy = true
  lifecycle {
    ignore_changes = all #issue with IAM perms, can grant tags/website but cant read, so ignore changes 
  }
}

resource "aws_s3_bucket" "output_s3" { #need somewhere to store output analytics files
  bucket = lower("${local.app_name}-output-bucket") #bucket name must be all lowercase
  tags = merge({
        Name        = lower("${local.app_name}-output-bucket") #bucket name must be all lowercase
        Environment = "${var.env}"
    }, local.default_tags
  )
  
  force_destroy = true
  lifecycle {
    ignore_changes = all #see above
  }
}



module "lambda_function" {
  source                  = "../modules/lambda"
  lambda_name             = "${local.app_name}-file-processor"
  role_name               = "${local.app_name}-file-processor-role"
  log_retention_in_days   = 14
  image_uri               = "${module.ecr_repo.repository_url}:latest"
  timeout                 = 15
  memory_size             = 256
  input_bucket_arn       = aws_s3_bucket.input_s3.arn 
  output_bucket_arn      = aws_s3_bucket.output_s3.arn #seems like terraform doesnt work well w/ env variables, so pass as normal var
  environment_variables   = {
    OUTPUT_BUCKET = aws_s3_bucket.output_s3.bucket # for the lambda to know where to put output
  }
  default_tags = local.default_tags
  
}

module "ecr_repo" {
  source    = "../modules/ecr-repo"
  repo_name = lower("${local.app_name}-ecr")
  default_tags = local.default_tags
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function.lambda_arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.input_s3.arn #it was id for some reason??changed to arn

  
}

resource "aws_s3_bucket_notification" "s3_notification" {
  bucket = aws_s3_bucket.input_s3.id
  lambda_function {
    lambda_function_arn = module.lambda_function.lambda_arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "" #u cant use wildcards or else it fails silently 
    filter_suffix       = ".csv"
  }
  depends_on = [aws_lambda_permission.allow_bucket] #have to setup permission before we make the bucket notification or else race condition
}
