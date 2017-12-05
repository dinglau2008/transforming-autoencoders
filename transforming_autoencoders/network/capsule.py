import tensorflow as tf


dense   = tf.layers.dense
sigmoid = tf.nn.sigmoid


class Capsule(object):

    def __init__(self, name, x, extra_input, input_dim, recognizer_dim, generator_dim, transformation):

        self.name = name

        # Hyper-parameters
        self.input_dim      = input_dim
        self.recognizer_dim = recognizer_dim
        self.generator_dim  = generator_dim

        # Transformation applied (whether 'translation' or 'affine')
        self.transformation = transformation

        # Placeholders
        self.x           = x
        self.extra_input = extra_input

        self._inference = None
        self._summaries = []

        self.inference

    @property
    def inference(self):
        if self._inference is None:

            recognition = dense(self.x, units=self.recognizer_dim, activation=sigmoid, name='recognition_layer')

            probability = dense(recognition, units=1, activation=sigmoid, name='probability')
            probability = tf.tile(probability, [1, self.input_dim])  # replicate probability s.t. it has input shape

            if self.transformation == 'translation':
                learnt_transformation = dense(recognition, units=2, activation=None, name='xy_prediction')
                learnt_transformation_extended = tf.add(learnt_transformation, self.extra_input)
            else:  # self.transformation == 'affine'
                learnt_transformation = dense(recognition, units=9, activation=None, name='xy_prediction')
                learnt_transformation = tf.reshape(learnt_transformation, shape=[-1, 3, 3])
                learnt_transformation_extended = tf.matmul(learnt_transformation, self.extra_input)
                learnt_transformation_extended = tf.layers.flatten(learnt_transformation_extended)
            generation = dense(learnt_transformation_extended,
                               units=self.generator_dim, activation=sigmoid, name='generator_layer')

            out = dense(generation, units=self.input_dim, activation=None, name='output')

            self._inference = tf.multiply(out, probability)

        return self._inference

    @property
    def summaries(self):
        if not self._summaries:
            output_reshaped = tf.reshape(self.inference, [-1, 28, 28, 1])
            self._summaries.append(tf.summary.image('{}_output'.format(self.name), output_reshaped))

        return self._summaries
