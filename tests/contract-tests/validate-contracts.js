#!/usr/bin/env node

/**
 * Contract Test Validator
 * 
 * Validates sample JSON payloads against their corresponding JSON schemas
 * to ensure data contracts are properly defined and samples are valid.
 */

const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

// Initialize AJV with strict mode and formats
const ajv = new Ajv({
  strict: true,
  allErrors: true,
  verbose: true,
  discriminator: true  // Enable discriminator support for oneOf
});
addFormats(ajv);

// Paths
const SCHEMAS_DIR = path.join(__dirname, '../../data/contracts');
const SAMPLES_DIR = path.join(SCHEMAS_DIR, 'samples');

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

// Test configuration - maps sample files to their schemas
const testCases = [
  {
    schema: 'raw_cost.schema.json',
    samples: ['raw_cost_aws.json']
  },
  {
    schema: 'normalized_cost.schema.json',
    samples: ['normalized_cost_aws.json']
  },
  {
    schema: 'allocated_cost.schema.json',
    samples: ['allocated_cost_example.json']
  },
  {
    schema: 'recommendation.schema.json',
    samples: ['recommendation_rightsizing.json']
  },
  {
    schema: 'event.schema.json',
    samples: [
      'event_budget_exceeded.json',
      'event_anomaly_spike.json',
      'event_waste_detected.json',
      'event_commitment_low_utilization.json'
    ]
  },
  {
    schema: 'workflow_execution.schema.json',
    samples: ['workflow_execution_completed.json']
  },
  {
    schema: 'integration_delivery.schema.json',
    samples: ['integration_delivery_slack.json']
  }
];

// Statistics
let stats = {
  totalTests: 0,
  passed: 0,
  failed: 0,
  errors: []
};

/**
 * Load and parse a JSON file
 */
function loadJSON(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    throw new Error(`Failed to load ${filePath}: ${error.message}`);
  }
}

/**
 * Validate a sample against a schema
 */
function validateSample(schemaPath, samplePath, verbose = false) {
  const schemaName = path.basename(schemaPath);
  const sampleName = path.basename(samplePath);
  
  stats.totalTests++;
  
  try {
    // Load schema and sample
    const schema = loadJSON(schemaPath);
    const sample = loadJSON(samplePath);
    
    // For event schema, we need to compile it only once
    // Remove the $id to avoid caching issues with oneOf
    const schemaForValidation = { ...schema };
    delete schemaForValidation.$id;
    
    // Compile schema
    const validate = ajv.compile(schemaForValidation);
    
    // Validate sample
    const valid = validate(sample);
    
    if (valid) {
      stats.passed++;
      console.log(`${colors.green}✓${colors.reset} ${sampleName} validates against ${schemaName}`);
      return true;
    } else {
      stats.failed++;
      const error = {
        schema: schemaName,
        sample: sampleName,
        errors: validate.errors
      };
      stats.errors.push(error);
      
      console.log(`${colors.red}✗${colors.reset} ${sampleName} ${colors.red}FAILED${colors.reset} validation against ${schemaName}`);
      
      if (verbose) {
        console.log(`${colors.yellow}  Validation errors:${colors.reset}`);
        validate.errors.forEach((err, idx) => {
          console.log(`  ${idx + 1}. ${err.instancePath || '/'}: ${err.message}`);
          if (err.params) {
            console.log(`     Params: ${JSON.stringify(err.params)}`);
          }
        });
      }
      
      return false;
    }
  } catch (error) {
    stats.failed++;
    const err = {
      schema: schemaName,
      sample: sampleName,
      errors: [{ message: error.message }]
    };
    stats.errors.push(err);
    
    console.log(`${colors.red}✗${colors.reset} Error testing ${sampleName}: ${error.message}`);
    return false;
  }
}

/**
 * Run all contract tests
 */
function runTests(verbose = false) {
  console.log(`${colors.cyan}======================================${colors.reset}`);
  console.log(`${colors.cyan}  FinOps Data Contract Tests${colors.reset}`);
  console.log(`${colors.cyan}======================================${colors.reset}\n`);
  
  // Validate each test case
  testCases.forEach(testCase => {
    const schemaPath = path.join(SCHEMAS_DIR, testCase.schema);
    console.log(`${colors.blue}Testing schema:${colors.reset} ${testCase.schema}`);
    
    testCase.samples.forEach(sampleFile => {
      const samplePath = path.join(SAMPLES_DIR, sampleFile);
      validateSample(schemaPath, samplePath, verbose);
    });
    
    console.log('');
  });
  
  // Print summary
  console.log(`${colors.cyan}======================================${colors.reset}`);
  console.log(`${colors.cyan}  Test Summary${colors.reset}`);
  console.log(`${colors.cyan}======================================${colors.reset}`);
  console.log(`Total tests: ${stats.totalTests}`);
  console.log(`${colors.green}Passed: ${stats.passed}${colors.reset}`);
  console.log(`${colors.red}Failed: ${stats.failed}${colors.reset}\n`);
  
  if (stats.failed > 0) {
    console.log(`${colors.red}Some tests failed. Use --verbose for details.${colors.reset}\n`);
    process.exit(1);
  } else {
    console.log(`${colors.green}All contract tests passed! ✓${colors.reset}\n`);
    process.exit(0);
  }
}

// Parse command line arguments
const verbose = process.argv.includes('--verbose') || process.argv.includes('-v');

// Run tests
runTests(verbose);
