import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Load data
data = pd.read_csv('network_traffic.csv')

# Handle missing values
for column in data.columns:
    if data[column].dtype == 'object':
        data[column].fillna(data[column].mode()[0], inplace=True)
    else:
        data[column].fillna(data[column].median(), inplace=True)

# Separate features and labels
features = data.drop(['timestamp', 'is_anomaly'], axis=1)  # Exclude 'is_anomaly'
labels = data['is_anomaly']  # Used only for evaluation

# Identify numerical and categorical columns
numerical_cols = features.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = features.select_dtypes(include=['object']).columns.tolist()

# Define preprocessing pipelines
numerical_pipeline = Pipeline([
    ('scaler', StandardScaler())
])

categorical_pipeline = Pipeline([
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer([
    ('num', numerical_pipeline, numerical_cols),
    ('cat', categorical_pipeline, categorical_cols)
])

# Create modeling pipeline
model_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('isolation_forest', IsolationForest(n_estimators=100, contamination=0.01, random_state=42))
])

# Fit the model
model_pipeline.fit(features)

# Save preprocessor and model separately
joblib.dump(model_pipeline.named_steps['preprocessor'], 'preprocessor.pkl')
joblib.dump(model_pipeline.named_steps['isolation_forest'], 'isolation_forest_model.pkl')

print("Model and preprocessor saved successfully.")
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Load data
data = pd.read_csv('network_traffic.csv')

# Handle missing values
for column in data.columns:
    if data[column].dtype == 'object':
        data[column].fillna(data[column].mode()[0], inplace=True)
    else:
        data[column].fillna(data[column].median(), inplace=True)

# Separate features and labels
features = data.drop(['timestamp', 'is_anomaly'], axis=1)  # Exclude 'is_anomaly'
labels = data['is_anomaly']  # Used only for evaluation

# Identify numerical and categorical columns
numerical_cols = features.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = features.select_dtypes(include=['object']).columns.tolist()

# Define preprocessing pipelines
numerical_pipeline = Pipeline([
    ('scaler', StandardScaler())
])

categorical_pipeline = Pipeline([
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer([
    ('num', numerical_pipeline, numerical_cols),
    ('cat', categorical_pipeline, categorical_cols)
])

# Create modeling pipeline
model_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('isolation_forest', IsolationForest(n_estimators=100, contamination=0.01, random_state=42))
])

# Fit the model
model_pipeline.fit(features)

# Save preprocessor and model separately
joblib.dump(model_pipeline.named_steps['preprocessor'], 'preprocessor.pkl')
joblib.dump(model_pipeline.named_steps['isolation_forest'], 'isolation_forest_model.pkl')

print("Model and preprocessor saved successfully.")
