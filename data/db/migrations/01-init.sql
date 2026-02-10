-- Initial database setup for FinOps SaaS Platform
-- This script runs automatically when PostgreSQL container starts

-- Create keycloak database for SSO/Auth service
CREATE DATABASE keycloak;
GRANT ALL PRIVILEGES ON DATABASE keycloak TO finops;

-- Log successful initialization
\echo 'FinOps databases initialized successfully'
