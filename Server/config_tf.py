import tensorflow as tf

# configure tensorflow for running on GPU, if present
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(allow_growth=True))
    session = tf.compat.v1.Session(config=config)
    tf.compat.v1.keras.backend.set_session(session)
