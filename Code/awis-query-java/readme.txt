-------------------------------------------------------------------------
-              Java Sample for Alexa Web Information Service            -
-------------------------------------------------------------------------
This sample will make a request to the Alexa Web Information Service
using an Access Key ID and Secret Access Key for an IAM user with a 
policy attached allowing usage of the service.

Tested with Java 1.8.0_141.

Steps:
1. Sign up for an Amazon Web Services account at http://aws.amazon.com
   (Note that you must have a valid credit card)
2. Create an IAM user and Get the Access Key ID and Secret Access Key
3. Create an IAM policy
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "awis:GET"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
4. Attach policy to the IAM user created previously
5. Uncompress the zip file into a working directory
6. Compile UrlInfo.java:

    javac UrlInfo.java

7. Run

    java UrlInfo ACCESS_KEY_ID SECRET_ACCESS_KEY site

If you are getting "Not Authorized" messages, you probably have one of the
following problems:

1. Your access key or secret key were not entered properly.  Please re-check
that they are correct.

2. You did not sign up for the Alexa Web Information Service at
http://aws.amazon.com/awis.  (This step is separate from signing
up for Amazon Web Services.)

3. Your credit card was not valid.

If you are getting "Request Expired" messages, please check that the date 
and time are properly set on your computer.
