import sys
import tensorflow as tf
from PIL import Image
from io import BytesIO

responseTime = 0
prediction = 0
x = 0
keep_prob = 0
sess = 0



def recNum(imgStr):
	imgArray = preProcess(imgStr)
	if isinstance(imgArray, str):
		return imgArray
	result = predict(imgArray)
	return result[0]


def preProcess(imgStr):
	"""预处理
	将图像区域找出来，将其缩放放置在28*28图像中的中央
	Arg:
		imgStr: 从web获取并解码好的数据
	Return:
		返回一个(1,28*28)大小的list，其是28*28图像reshape而成
	"""
	try:
		#将数据解码成pil的image
		img = Image.open(BytesIO(imgStr)).convert('L')
	except:
		return "nothing"

	#找出数字所在区域的最小外接矩形
	bbox = Image.eval(img, lambda px: 255-px).getbbox()
	if bbox is None:
		return "nothing"

	#将区域按比例缩小，最大边为20
	widthlen = bbox[2] - bbox[0]
	heightlen = bbox[3] - bbox[1]

	if(heightlen > widthlen):
		widthlen = int(20.0*widthlen/heightlen)
		heightlen = 20
	else:
		heightlen = int(20.0*heightlen/widthlen)
		widthlen = 20
	hstart = int((28 - heightlen)/2)
	wstart = int((28 - widthlen)/2)

	#TODO(ww): 这里nearest参数效果比默认参数好，还需探究
	img = img.crop(bbox).resize((widthlen, heightlen), Image.NEAREST)

	smallImg = Image.new('L', (28,28), 255)
	smallImg.paste(img, (wstart, hstart))
	imgdata = list(smallImg.getdata())
	#需要改为背景为0，前景为1
	imgdata = [(255.0-x)/255.0 for x in imgdata]
	return imgdata

def predict(imgArray):
	"""预测
	通过加载好的模型来进行预测
	Return:
		预测值的list
	"""
	global responseTime, prediction, sess, x, keep_prob
	#程序加载的第一次进行预测初始化，之后就调用全局变量
	if(responseTime == 0):
		predictInit()
		responseTime = 1
	return prediction.eval(feed_dict={x: [imgArray],keep_prob: 1.0}, session=sess)

def predictInit():
	"""预测初始化
	初始化各种参数和加载训练好的模型，一些参数需要声明为全局变量，不需要多次加载
	"""
	global prediction, sess, x, keep_prob
	x = tf.placeholder(tf.float32, [None, 784])
	W = tf.Variable(tf.zeros([784, 10]))
	b = tf.Variable(tf.zeros([10]))

	def weight_variable(shape):
		initial = tf.truncated_normal(shape, stddev=0.1)
		return tf.Variable(initial)

	def bias_variable(shape):
		initial = tf.constant(0.1, shape=shape)
		return tf.Variable(initial)
	   
	def conv2d(x, W):
		return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

	def max_pool_2x2(x):
		return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')   

	W_conv1 = weight_variable([5, 5, 1, 32])
	b_conv1 = bias_variable([32])

	x_image = tf.reshape(x, [-1,28,28,1])
	h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
	h_pool1 = max_pool_2x2(h_conv1)

	W_conv2 = weight_variable([5, 5, 32, 64])
	b_conv2 = bias_variable([64])

	h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
	h_pool2 = max_pool_2x2(h_conv2)

	W_fc1 = weight_variable([7 * 7 * 64, 1024])
	b_fc1 = bias_variable([1024])

	h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
	h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

	keep_prob = tf.placeholder(tf.float32)
	h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

	W_fc2 = weight_variable([1024, 10])
	b_fc2 = bias_variable([10])

	y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

	init_op = tf.initialize_all_variables()
	saver = tf.train.Saver()


	sess = tf.Session()
	sess.run(init_op)
	saver.restore(sess, "digits_recognition/model/model.ckpt")
	prediction = tf.argmax(y_conv,1)
	


