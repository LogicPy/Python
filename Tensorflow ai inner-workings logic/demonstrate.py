import tensorflow as tf

def default_hparams():
    return {
        'n_ctx': 1024,
        'n_embd': 512,
        'n_vocab': 10000,
        'n_layer': 12,
        'n_head': 16,
    }

def model(hparams, X, past=None, scope='model'):
    with tf.name_scope(scope):
        # Define embedding layer
        wpe = tf.Variable(tf.random.normal([hparams['n_vocab'], hparams['n_embd']]), name="wpe")
        
        # Apply embedding lookup
        X_emb = tf.nn.embedding_lookup(wpe, X)
        
        # Add positional encoding
        position = tf.range(tf.shape(X_emb)[1], dtype=tf.float32)
        position = tf.expand_dims(position, axis=1)
        position = tf.expand_dims(position, axis=0)

        d_model = tf.cast(hparams['n_embd'], tf.float32)
        angle_rates = 1 / tf.pow(10000, (2 * (tf.range(d_model, dtype=tf.float32) // 2)) / d_model)
        angle_rads = position * angle_rates

        sine = tf.sin(angle_rads[:, :, 0::2])
        cosine = tf.cos(angle_rads[:, :, 1::2])

        pos_encoding = tf.concat([sine, cosine], axis=-1)
        pos_encoding = tf.tile(pos_encoding, [tf.shape(X_emb)[0], 1, 1])  # Match batch size
        X_emb += pos_encoding
        
        present_state = None
        if past is not None:
            present_state = [tf.keras.layers.LayerNormalization()(p) for p in past['present']]
            
            # Compute attention weights and apply them to input sequence
            attention_weights = tf.keras.layers.Dense(hparams['n_head'])(X_emb)
            X_emb += tf.matmul(attention_weights, X_emb)
        
        logits = tf.keras.layers.Dense(hparams['n_vocab'])(X_emb)
        
        return {
            'logits': logits,
            'present': present_state,
        }

# Define input sequence
X = tf.random.uniform((1, 10), maxval=10000, dtype=tf.int32)

# Create model instance
hparams_instance = default_hparams()
model_instance = model(hparams_instance, X)

# Get output logits and present state
logits = model_instance['logits']
present_state = model_instance['present']

print(logits.shape)  # Output shape
if present_state is not None:
    print(present_state[0].shape)  # Output shape if present_state is not None
