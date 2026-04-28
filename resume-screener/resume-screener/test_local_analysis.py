#!/usr/bin/env python3
"""Test script to verify local analysis works without API keys"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import analyze_resumes_locally

# Test data
job_description = """
Senior Python Developer with 5+ years of experience. 
Must have Python, Django, PostgreSQL, Docker, AWS experience. 
Strong knowledge of REST APIs and microservices required.
"""

resumes = [
    {
        "name": "John_Doe.pdf", 
        "text": "John Doe is a Senior Python Developer with 6 years of experience. He has worked with Django, PostgreSQL, Docker, and AWS. He has built REST APIs and microservices."
    },
    {
        "name": "Jane_Smith.pdf", 
        "text": "Jane Smith is a Java Developer with 3 years of experience. She has worked with Spring Boot and MySQL. She has some experience with Docker."
    }
]

if __name__ == "__main__":
    print("Testing local resume analysis...")
    results = analyze_resumes_locally(job_description, resumes)
    
    print(f"\nAnalyzed {len(results)} resumes:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['name']}")
        print(f"   Role: {result['role']}")
        print(f"   Score: {result['score']}%")
        print(f"   Skills Matched: {', '.join(result['skills_matched'])}")
        print(f"   Skills Missing: {', '.join(result['skills_missing'])}")
        print(f"   Summary: {result['summary']}")
    
    print("\n✅ Local analysis test completed successfully!")
