# Lambda IAM Role
resource "aws_iam_role" "lambda_exec_role" {
  name = var.role_name
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.default_tags
}

resource "aws_iam_role_policy" "lambda_give_s3_access" {
  name = "${var.role_name}-bucket-access"
  role = aws_iam_role.lambda_exec_role.name
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid = "InputBucketList", #perms for input bucket
        Effect = "Allow",
        Action = ["s3:ListBucket"],
        Resource = [var.input_bucket_arn]
      },
      {
        Sid = "InputBucketObjects", #perms for input bucket objs
        Effect = "Allow",
        Action = ["s3:GetObject"],
        Resource = ["${var.input_bucket_arn}/*"]
      },
      {
        Sid = "OutputBucketList", #perms for output bucket
        Effect = "Allow",
        Action = ["s3:ListBucket"],
        Resource = [var.output_bucket_arn]
      },
      {
        Sid = "OutputBucketObjects", #perms for output bucket objs
        Effect = "Allow",
        Action = ["s3:PutObject"],
        Resource = ["${var.output_bucket_arn}/*"]
      }
    ]
  })
}
#lambda doesnt appear to have perms to do s3 actions so have to manually grant 

# Attach the basic execution policy for CloudWatch Logs
resource "aws_iam_role_policy_attachment" "lambda_logging" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = var.log_retention_in_days
  tags = var.default_tags #has to be logged to be viewable
}

# Lambda Function
resource "aws_lambda_function" "lambda_function" {
  function_name = var.lambda_name
  role          = aws_iam_role.lambda_exec_role.arn
  package_type  = "Image"
  image_uri     = var.image_uri
  
  image_config {
    command = ["analytics_app.lambda_handler" ] #i had an issue when i tried to run the file in LocalStack
    #python has "lambda" as reserved so i just renamed it
  }
  
  timeout       = var.timeout
  memory_size   = var.memory_size

  environment {
    variables = var.environment_variables
  }

  tags = var.default_tags
}

