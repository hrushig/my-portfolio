import boto3
import StringIO
import zipfile
import mimetypes
import boto3

def lambda_handler(event, context):

    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:776941257690:deployPortfolioTopic')

    try:
        portfolio_bucket = s3.Bucket('portfolio.warriors-hg.co.uk')
        build_bucket = s3.Bucket('portfoliobuild.warriors-hg.co.uk')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                  ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        print("Job Done!")
        topic.publish(Subject="Build Deployment Success", Message="Build has been deployed successfully")
    except:
        topic.publish(Subject="Build Deployment Failure", Message="Build failed to deploy")
        raise
    return ("build")
