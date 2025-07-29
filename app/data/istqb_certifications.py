# ISTQB Certification Data and Knowledge Base

certifications = {
    # Foundation Level
    'CTFL': {
        'id': 'CTFL',
        'name': 'Certified Tester Foundation Level',
        'level': 'Foundation',
        'type': 'Core',
        'description': 'The Foundation Level forms the basis of the ISTQB® Certified Tester Scheme. It provides fundamental testing knowledge for all software testing roles.',
        'prerequisites': ['None - Entry level certification'],
        'experienceRequired': 'None (recommended: some basic testing exposure)',
        'examFormat': {
            'questions': 40,
            'duration': '65 minutes',
            'passingScore': '65% (26/40)',
            'type': 'Multiple choice'
        },
        'targetAudience': [
            'New testers',
            'Developers moving to testing',
            'Project managers',
            'Quality assurance professionals',
            'Business analysts'
        ],
        'topics': [
            'Fundamentals of Testing',
            'Testing Throughout the Software Development Lifecycle',
            'Static Testing',
            'Test Techniques',
            'Test Management',
            'Tool Support for Testing'
        ],
        'careerValue': 'Essential first step, globally recognized, opens doors to advanced certifications',
        'estimatedStudyTime': '40-60 hours',
        'averageCost': '$200-400'
    },

    # Advanced Level
    'CTAL-TA': {
        'id': 'CTAL-TA',
        'name': 'Certified Tester Advanced Level Test Analyst',
        'level': 'Advanced',
        'type': 'Core',
        'description': 'Provides skills needed to perform structured and thorough software testing across the software development lifecycle.',
        'prerequisites': ['CTFL certification required'],
        'experienceRequired': '18 months testing experience (recommended)',
        'examFormat': {
            'questions': 65,
            'duration': '180 minutes',
            'passingScore': '65%',
            'type': 'Multiple choice'
        },
        'targetAudience': [
            'Test analysts',
            'Senior testers',
            'QA leads',
            'Testing consultants'
        ],
        'topics': [
            'The Test Analyst\'s Tasks in Risk-Based Testing',
            'Test Techniques',
            'Testing of Software Quality Characteristics',
            'Reviews',
            'Incident Management',
            'Test Progress Monitoring and Control',
            'Test Tools and Automation'
        ],
        'careerValue': 'Significant career advancement, higher salary potential, technical leadership roles',
        'estimatedStudyTime': '80-120 hours',
        'averageCost': '$500-800'
    },

    'CTAL-TM': {
        'id': 'CTAL-TM',
        'name': 'Certified Tester Advanced Level Test Manager',
        'level': 'Advanced',
        'type': 'Core',
        'description': 'Focuses on test management skills for leading testing teams and managing testing projects.',
        'prerequisites': ['CTFL certification required'],
        'experienceRequired': '18 months testing experience with management responsibilities',
        'examFormat': {
            'questions': 65,
            'duration': '180 minutes',
            'passingScore': '65%',
            'type': 'Multiple choice'
        },
        'targetAudience': [
            'Test managers',
            'QA managers',
            'Project managers',
            'Team leads',
            'Testing consultants'
        ],
        'topics': [
            'Testing Process',
            'Test Management',
            'Risk-Based Testing',
            'Test Progress Monitoring and Control',
            'Incident Management',
            'Evaluating and Improving Test Processes',
            'Test Tools and Automation'
        ],
        'careerValue': 'Management track advancement, team leadership, strategic planning skills',
        'estimatedStudyTime': '80-120 hours',
        'averageCost': '$500-800'
    },

    'CTAL-TAE': {
        'id': 'CTAL-TAE',
        'name': 'Certified Tester Advanced Level Test Automation Engineering',
        'level': 'Advanced',
        'type': 'Core',
        'description': 'Targeted to test engineers looking to implement or improve test automation.',
        'prerequisites': ['CTFL certification required'],
        'experienceRequired': '18 months testing experience with automation exposure',
        'examFormat': {
            'questions': 65,
            'duration': '180 minutes',
            'passingScore': '65%',
            'type': 'Multiple choice'
        },
        'targetAudience': [
            'Test automation engineers',
            'Senior developers in testing',
            'Technical test leads',
            'DevOps engineers'
        ],
        'topics': [
            'Introduction and Objectives for Test Automation',
            'Preparing for Test Automation',
            'The Generic Test Automation Architecture',
            'Test Automation Deployment and Maintenance',
            'Test Automation Reporting and Metrics',
            'Transitioning Manual Testing to an Automated Environment'
        ],
        'careerValue': 'High demand specialization, technical leadership, automation expertise',
        'estimatedStudyTime': '100-140 hours',
        'averageCost': '$500-800'
    },

    # Specialist Certifications
    'CT-MAT': {
        'id': 'CT-MAT',
        'name': 'Certified Tester Mobile Application Testing',
        'level': 'Specialist',
        'type': 'Specialist',
        'description': 'Provides insight into methods, techniques, and tools for testing mobile applications.',
        'prerequisites': ['CTFL certification required'],
        'experienceRequired': 'Mobile testing experience recommended',
        'examFormat': {
            'questions': 40,
            'duration': '90 minutes',
            'passingScore': '65%',
            'type': 'Multiple choice'
        },
        'targetAudience': [
            'Mobile app testers',
            'QA engineers in mobile development',
            'Test analysts working on mobile projects'
        ],
        'topics': [
            'Mobile Application Testing Strategy',
            'Mobile Application Test Types',
            'Mobile Application Test Environments',
            'Mobile Application Test Automation',
            'Mobile Application Testing Tools'
        ],
        'careerValue': 'Mobile expertise in high demand, specialized skills, competitive advantage',
        'estimatedStudyTime': '60-80 hours',
        'averageCost': '$400-600'
    },

    'CT-AI': {
        'id': 'CT-AI',
        'name': 'Certified Tester AI Testing',
        'level': 'Specialist',
        'type': 'Specialist',
        'description': 'Focuses on testing AI-based and ML systems, covering unique challenges and approaches.',
        'prerequisites': ['CTFL certification required'],
        'experienceRequired': 'AI/ML project exposure recommended',
        'examFormat': {
            'questions': 40,
            'duration': '90 minutes',
            'passingScore': '65%',
            'type': 'Multiple choice'
        },
        'targetAudience': [
            'Testers working with AI systems',
            'QA engineers in AI/ML teams',
            'Test analysts in data science projects'
        ],
        'topics': [
            'AI and ML Fundamentals for Testers',
            'Testing AI-based Systems',
            'Test Data for AI Systems',
            'AI Testing Tools and Techniques',
            'Ethics and Bias in AI Testing'
        ],
        'careerValue': 'Cutting-edge specialization, future-proof skills, high market value',
        'estimatedStudyTime': '70-90 hours',
        'averageCost': '$500-700'
    },

    'CT-AuT': {
        'id': 'CT-AuT',
        'name': 'Certified Tester Automotive Software Tester',
        'level': 'Specialist',
        'type': 'Specialist',
        'description': 'Covers specific requirements for testing E/E systems in the automotive environment.',
        'prerequisites': ['CTFL certification required'],
        'experienceRequired': 'Automotive industry experience recommended',
        'examFormat': {
            'questions': 40,
            'duration': '90 minutes',
            'passingScore': '65%',
            'type': 'Multiple choice'
        },
        'targetAudience': [
            'Automotive software testers',
            'Embedded systems testers',
            'QA engineers in automotive companies'
        ],
        'topics': [
            'Automotive Software Development',
            'Automotive Testing Standards',
            'Safety and Security Testing',
            'Automotive Test Environments',
            'Automotive Testing Tools'
        ],
        'careerValue': 'Specialized industry knowledge, automotive sector opportunities',
        'estimatedStudyTime': '60-80 hours',
        'averageCost': '$400-600'
    }
}

training_providers = [
    {
        'id': 'astqb',
        'name': 'American Software Testing Qualifications Board (ASTQB)',
        'website': 'https://astqb.org',
        'type': 'Official Board',
        'description': 'Official ISTQB member board for the United States',
        'coursesOffered': ['CTFL', 'CTAL-TA', 'CTAL-TM', 'CTAL-TAE', 'CT-MAT', 'CT-AI'],
        'formats': ['Self-study', 'Online courses', 'In-person workshops'],
        'regions': ['North America']
    },
    {
        'id': 'istqb-official',
        'name': 'ISTQB Official Partners',
        'website': 'https://istqb.org',
        'type': 'Official Partners',
        'description': 'Network of ISTQB-accredited training providers worldwide',
        'coursesOffered': ['All ISTQB certifications'],
        'formats': ['Instructor-led', 'Online', 'Blended learning'],
        'regions': ['Global']
    },
    {
        'id': 'udemy',
        'name': 'Udemy',
        'website': 'https://udemy.com',
        'type': 'Online Platform',
        'description': 'Popular online learning platform with various ISTQB prep courses',
        'coursesOffered': ['CTFL', 'CTAL-TA', 'CTAL-TM'],
        'formats': ['Self-paced online'],
        'regions': ['Global'],
        'priceRange': '$50-200'
    },
    {
        'id': 'coursera',
        'name': 'Coursera',
        'website': 'https://coursera.org',
        'type': 'Online Platform',
        'description': 'University-partnered online courses including ISTQB preparation',
        'coursesOffered': ['CTFL', 'CTAL-TA'],
        'formats': ['Self-paced', 'Guided courses'],
        'regions': ['Global'],
        'priceRange': '$39-79/month'
    },
    {
        'id': 'pluralsight',
        'name': 'Pluralsight',
        'website': 'https://pluralsight.com',
        'type': 'Tech Platform',
        'description': 'Technology-focused learning platform with testing courses',
        'coursesOffered': ['CTFL', 'CTAL-TAE'],
        'formats': ['Self-paced online'],
        'regions': ['Global'],
        'priceRange': '$45/month'
    }
]

career_paths = {
    'junior-tester': {
        'experience': '0-2 years',
        'recommendedPath': ['CTFL'],
        'description': 'Start with Foundation Level to build fundamental testing knowledge'
    },
    'test-analyst': {
        'experience': '2-5 years',
        'recommendedPath': ['CTFL', 'CTAL-TA'],
        'description': 'Progress to Advanced Test Analyst for technical depth'
    },
    'test-manager': {
        'experience': '3-7 years',
        'recommendedPath': ['CTFL', 'CTAL-TM'],
        'description': 'Move into management track with Test Manager certification'
    },
    'automation-engineer': {
        'experience': '2-6 years',
        'recommendedPath': ['CTFL', 'CTAL-TAE'],
        'description': 'Specialize in automation with Test Automation Engineering'
    },
    'senior-specialist': {
        'experience': '5+ years',
        'recommendedPath': ['CTFL', 'Advanced Level', 'Specialist Certifications'],
        'description': 'Combine advanced and specialist certifications for expertise'
    }
}
