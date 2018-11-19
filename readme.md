# Rekognition 是AWS的一个人工只能图像识别API服务
本Demo演示，上传人脸图片建立图像库，应用时上传视频内容到S3，触发Rekognition分析视频，找出匹配的人脸。
结果录入DynamoDB，原始结果保存在S3，结构图如下：
![结构图](https://github.com/hawkey999/aws-rekognition-video-face-detection-demo/blob/master/Architect.png
)

详细见Rekognition API文档 https://docs.aws.amazon.com/zh_cn/rekognition/latest/dg/API_Operations.html
此处主要使用四个接口：
* CreateCollection() 见人脸索引库
* IndexFaces() 上传人脸，建信息索引
* StartFaceSearch() 触发分析
* GetFaceSearch() 获取分析结果

# Prepare resource
* create S3 bucket e.g. rekognition-demo-video-oregon
	with 3 folders: img-index-input, video-input, video-result

* create rekognition collection, note down the ARN
	aws rekognition create-collection --collection-id video-face-search
	aws:rekognition:us-west-2:9684xxxxxx1:collection/video-face-search

* create SNS topic, note down the ARN: 
	arn:aws:sns:us-west-2:9684xxxxxx1:rekognition-demo-video-face-search

* create Rekognition role: authorized to publish sns topic
	arn:aws:iam::9684xxxxxx1:role/Rekognition_service_role

* create IAM role for Lambda, authorized to call: rekognition, DDB, S3, IAM passrole

* create DDB table to record index, videoResult and face: 
	rekognition-demo-user-img-index, rekognition-demo-video-result, rekognition-demo-video-face-matched

* for demo: create DDB record with s3key, e.g. img-index-input/xxx.jpg and user_id 10001002010

# Create Lambda
* rekognition-demo-s3-img-index-to-rekognition
	-trigger by s3 with prefix: img-index-input/ suffix: .jpg

* rekognition-demo-s3-video-to-rekognition
	-trigger by s3 with prefix: video-input/ suffix: .mp4
	这里置信度设置为75，可以自行修改 FaceMatchThreshold=75,

* rekognition-demo-get-result
	-trigger by SNS
	这里最大结果如果超过MaxResults，本例中设置MaxResults=1000，则会收到响应中有NextToken
	需要依据响应的NextToken去获取下一段结果

# Test
* img
	e.g. rekognition-demo-huangzb/img-index-input/JamesHuang.jpg

* List face and delete face command:
	aws rekognition list-faces --collection-id video-face-search
	aws rekognition delete-faces --collection-id video-face-search --face-ids 2d66d885-e35e-4cb1-9952-dd04b7cb5aed

* Test with upload video to S3, e.g. rekognition-demo-huang/xxxxxx.mp4
