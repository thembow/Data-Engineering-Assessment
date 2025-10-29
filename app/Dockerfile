# Use an official Python image as the base
FROM public.ecr.aws/lambda/python:3.9

# Copy the current directory contents into the container
COPY . ${LAMBDA_TASK_ROOT}

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Set the default command to run when the container starts
CMD ["analytics_app.lambda_handler"]