from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict
from app.data.istqb_certifications import certifications, training_providers
from app.models import CertificationRecommendation, TrainingProvider
from app.middleware.auth import verify_token


router = APIRouter()


@router.get("/", response_model=List[Dict[str, Optional[str]]])
async def get_certifications(current_user: dict = Depends(verify_token)):
    """Get list of all ISTQB certifications"""
    try:
        cert_list = []
        for cert in certifications.values():
            cert_list.append({
                "id": cert['id'],
                "name": cert['name'],
                "level": cert['level'],
                "type": cert['type'],
                "description": cert['description'],
                "prerequisites": ', '.join(cert['prerequisites'])
            })
        
        return cert_list
    except Exception as error:
        print(f"Get certifications error: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to retrieve certifications",
                "message": str(error)
            }
        )


@router.get("/recommendations", response_model=List[CertificationRecommendation])
async def get_recommendations(experience: Optional[str] = None, role: Optional[str] = None, current_user: dict = Depends(verify_token)):
    """Get certification recommendations"""
    try:
        recommendations = []

        if experience:
            exp_years = int(experience)
            if exp_years <= 2:
                recommendations.append(
                    CertificationRecommendation(
                        certification=certifications['CTFL'],
                        reason='Perfect starting point for building fundamental testing knowledge',
                        priority='High'
                    )
                )
            elif 2 < exp_years <= 5:
                recommendations.append(
                    CertificationRecommendation(
                        certification=certifications['CTAL-TA'],
                        reason='Advance your technical testing skills with Test Analyst certification',
                        priority='High'
                    )
                )
            elif exp_years > 5:
                recommendations.append(
                    CertificationRecommendation(
                        certification=certifications['CTAL-TAE'],
                        reason='Automation expertise is in high demand for senior professionals',
                        priority='High'
                    )
                )

        if role:
            role_upper = role.upper()
            if 'MANAGER' in role_upper or 'LEAD' in role_upper:
                recommendations.append(
                    CertificationRecommendation(
                        certification=certifications['CTAL-TM'],
                        reason='Essential for testing leadership and management roles',
                        priority='High'
                    )
                )
            if 'AUTOMATION' in role_upper or 'DEVOPS' in role_upper:
                recommendations.append(
                    CertificationRecommendation(
                        certification=certifications['CTAL-TAE'],
                        reason='Perfect match for your automation-focused role',
                        priority='High'
                    )
                )

        if not recommendations:
            recommendations.append(
                CertificationRecommendation(
                    certification=certifications['CTFL'],
                    reason='Foundation Level is the recommended starting point for all ISTQB certifications',
                    priority='High'
                )
            )

        return recommendations
    except Exception as error:
        print(f"Get recommendations error: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to generate recommendations",
                "message": str(error)
            }
        )


@router.get("/training-providers", response_model=List[TrainingProvider])
async def get_training_providers(certification: Optional[str] = None, format: Optional[str] = None, region: Optional[str] = None, current_user: dict = Depends(verify_token)):
    """Get list of accredited training providers"""
    try:
        filtered_providers = training_providers

        if certification:
            filtered_providers = [
                provider for provider in filtered_providers
                if certification.upper() in provider['coursesOffered'] or provider['coursesOffered'] == 'All ISTQB certifications'
            ]

        if format:
            filtered_providers = [
                provider for provider in filtered_providers
                if any(f.lower() in format.lower() for f in provider['formats'])
            ]

        if region:
            filtered_providers = [
                provider for provider in filtered_providers
                if any(r.lower() in region.lower() for r in provider['regions']) or 'Global' in provider['regions']
            ]

        return filtered_providers
    except Exception as error:
        print(f"Get training providers error: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to retrieve training providers",
                "message": str(error)
            }
        )
        
