from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone


# Assessment questions oriented for Ukrainian veterans transitioning to civilian careers.
# Each entry: id, question, type, optional choices. Keep content generic and optional
# to respect privacy; all fields are optional in the model.
ASSESSMENT_QUESTIONS = [
	{"id": "service_branch", "question": "Which branch of the armed forces did you serve in?", "type": "text"},
	{"id": "service_role", "question": "What was your primary role / military occupation specialty?", "type": "text"},
	{"id": "rank", "question": "What was your rank at discharge?", "type": "text"},
	{"id": "years_of_service", "question": "How many years did you serve?", "type": "number"},
	{"id": "discharge_date", "question": "When were you discharged (approximate year)?", "type": "text"},
	{"id": "deployment_experience", "question": "Have you been deployed on operations?", "type": "choice", "choices": ["Yes", "No"]},
	{"id": "leadership_experience", "question": "Did you have leadership or management responsibilities?", "type": "choice", "choices": ["Yes", "No"]},
	{"id": "primary_skills", "question": "What are your main technical or professional skills (comma-separated)?", "type": "text"},
	{"id": "civilian_certifications", "question": "Do you hold any civilian or military-to-civilian certifications (IT, logistics, medical, trades)?", "type": "text"},
	{"id": "education_level", "question": "What is your highest civilian education level?", "type": "choice", "choices": ["No formal education", "Secondary", "Vocational/Technical", "Bachelors", "Masters+"]},
	{"id": "disabilities_or_limits", "question": "Do you have any service-related injuries or limitations the advisor should consider?", "type": "text"},
	{"id": "security_clearance", "question": "Do you hold any security clearance that could affect employment?", "type": "choice", "choices": ["Yes", "No", "Not sure"]},
	{"id": "current_goals", "question": "What are your short-term professional goals (next 6-12 months)?", "type": "text"},
	{"id": "long_term_goals", "question": "What are your long-term goals (3-5 years)?", "type": "text"},
	{"id": "work_preferences", "question": "Which working arrangements do you prefer?", "type": "choice", "choices": ["Full-time employment", "Freelance/Contract", "Start my own business", "Public sector", "Undecided"]},
	{"id": "financial_needs", "question": "Do you need immediate steady income or can you wait to build something?", "type": "choice", "choices": ["Immediate steady income", "Can wait to build", "Flexible"]},
	{"id": "locality", "question": "Which region/city are you planning to work in (affects opportunities)?", "type": "text"},
	{"id": "available_time", "question": "How much time per week can you dedicate to training or building a business?", "type": "choice", "choices": ["<10 hours", "10-20 hours", "20-40 hours", ">40 hours"]},
	{"id": "benefits_awareness", "question": "Are you aware of veteran benefits / support programs you can access?", "type": "choice", "choices": ["Yes", "Somewhat", "No"]},
	{"id": "support_needs", "question": "Do you need support with housing, medical care, mental health, or legal assistance?", "type": "text"},
	{"id": "additional_info", "question": "Anything else the advisor should know (privacy-sensitive info optional)?", "type": "text"},
]


class UserAssessment(models.Model):
	"""Stores a user's answers to an advisor assessment and summary fields.

	The `answers` JSON field keeps original question->answer data so the raw
	responses are preserved for later analysis or prompting LLMs. There are
	also convenience fields (experience, skills, preferred_path, suggested_path)
	to make querying and summarization simpler.
	"""

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessments')
	answers = models.JSONField(default=dict, blank=True)

	# Convenience / indexed fields
	# General career fields
	experience_level = models.CharField(max_length=255, blank=True, null=True)
	experience_years = models.IntegerField(blank=True, null=True)
	primary_skills = models.TextField(blank=True, null=True)
	work_preferences = models.CharField(max_length=255, blank=True, null=True)

	# The advisor/automation suggested path for the user (e.g. 'freelance', 'employment', 'business', 'undecided')
	suggested_path = models.CharField(max_length=255, blank=True, null=True)

	# Veteran-specific optional fields (focused on Ukrainian veterans)
	service_branch = models.CharField(max_length=255, blank=True, null=True)
	service_role = models.CharField(max_length=500, blank=True, null=True)
	rank = models.CharField(max_length=255, blank=True, null=True)
	years_of_service = models.IntegerField(blank=True, null=True)
	discharge_date = models.CharField(max_length=100, blank=True, null=True)
	deployment_experience = models.BooleanField(default=False)
	leadership_experience = models.BooleanField(default=False)
	civilian_certifications = models.TextField(blank=True, null=True)
	disabilities_or_limits = models.TextField(blank=True, null=True)
	security_clearance = models.CharField(max_length=255, blank=True, null=True)
	education_level = models.CharField(max_length=255, blank=True, null=True)
	locality = models.CharField(max_length=255, blank=True, null=True)
	benefits_awareness = models.CharField(max_length=255, blank=True, null=True)
	support_needs = models.TextField(blank=True, null=True)

	completed = models.BooleanField(default=False)

	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'user_assessments'

	def __str__(self):
		return f"Assessment {self.id} for {self.user}"

	def save(self, *args, **kwargs):
		# Try to keep convenience fields in sync with answers if provided
		if self.answers:
			# general fields
			if not self.experience_level and 'experience_level' in self.answers:
				self.experience_level = self.answers.get('experience_level')
			if not self.experience_years and 'experience_years' in self.answers:
				try:
					self.experience_years = int(self.answers.get('experience_years') or 0)
				except (TypeError, ValueError):
					self.experience_years = None
			if not self.primary_skills and 'primary_skills' in self.answers:
				self.primary_skills = self.answers.get('primary_skills')
			if not self.work_preferences and 'work_preferences' in self.answers:
				self.work_preferences = self.answers.get('work_preferences')

			# veteran-specific sync (optional)
			if not self.service_branch and 'service_branch' in self.answers:
				self.service_branch = self.answers.get('service_branch')
			if not self.service_role and 'service_role' in self.answers:
				self.service_role = self.answers.get('service_role')
			if not self.rank and 'rank' in self.answers:
				self.rank = self.answers.get('rank')
			if not self.years_of_service and 'years_of_service' in self.answers:
				try:
					self.years_of_service = int(self.answers.get('years_of_service') or 0)
				except (TypeError, ValueError):
					self.years_of_service = None
			if not self.discharge_date and 'discharge_date' in self.answers:
				self.discharge_date = self.answers.get('discharge_date')
			if 'deployment_experience' in self.answers:
				self.deployment_experience = True if str(self.answers.get('deployment_experience')).lower() in ['yes', 'true', '1'] else False
			if 'leadership_experience' in self.answers:
				self.leadership_experience = True if str(self.answers.get('leadership_experience')).lower() in ['yes', 'true', '1'] else False
			if not self.civilian_certifications and 'civilian_certifications' in self.answers:
				self.civilian_certifications = self.answers.get('civilian_certifications')
			if not self.disabilities_or_limits and 'disabilities_or_limits' in self.answers:
				self.disabilities_or_limits = self.answers.get('disabilities_or_limits')
			if not self.security_clearance and 'security_clearance' in self.answers:
				self.security_clearance = self.answers.get('security_clearance')
			if not self.education_level and 'education_level' in self.answers:
				self.education_level = self.answers.get('education_level')
			if not self.locality and 'locality' in self.answers:
				self.locality = self.answers.get('locality')
			if not self.benefits_awareness and 'benefits_awareness' in self.answers:
				self.benefits_awareness = self.answers.get('benefits_awareness')
			if not self.support_needs and 'support_needs' in self.answers:
				self.support_needs = self.answers.get('support_needs')

		super().save(*args, **kwargs)

	def to_llm_context(self) -> str:
		"""Return a concise, human-readable summary suitable for LLM prompt context.

		This method intentionally produces a short plain-text summary highlighting
		experience, skills, goals, and the user's work preference. Keep the output
		compact because it will be appended to LLM prompts.
		"""
		parts = []
		if self.experience_level:
			parts.append(f"Experience level: {self.experience_level}.")
		if self.experience_years is not None:
			parts.append(f"Years of experience: {self.experience_years}.")
		if self.primary_skills:
			parts.append(f"Primary skills: {self.primary_skills}.")
		if self.work_preferences:
			parts.append(f"Work preferences: {self.work_preferences}.")
		# Veteran-specific details (kept concise and optional)
		if self.service_branch:
			parts.append(f"Service branch: {self.service_branch}.")
		if self.service_role:
			parts.append(f"Service role: {self.service_role}.")
		if self.rank:
			parts.append(f"Rank at discharge: {self.rank}.")
		if self.years_of_service is not None:
			parts.append(f"Years of service: {self.years_of_service}.")
		if self.deployment_experience:
			parts.append("Deployment experience: yes.")
		if self.leadership_experience:
			parts.append("Leadership experience: yes.")
		if self.civilian_certifications:
			parts.append(f"Certifications: {self.civilian_certifications}.")
		if self.disabilities_or_limits:
			parts.append("Has service-related limitations (details withheld).")
		if self.security_clearance:
			parts.append(f"Security clearance status: {self.security_clearance}.")
		if self.education_level:
			parts.append(f"Education: {self.education_level}.")
		if self.locality:
			parts.append(f"Locality: {self.locality}.")
		if self.benefits_awareness:
			parts.append(f"Benefits awareness: {self.benefits_awareness}.")
		if self.support_needs:
			parts.append("Reported support needs (housing/medical/mental/legal).")
		goals = self.answers.get('current_goals') if isinstance(self.answers, dict) else None
		if goals:
			parts.append(f"Short-term goals: {goals}.")
		long_goals = self.answers.get('long_term_goals') if isinstance(self.answers, dict) else None
		if long_goals:
			parts.append(f"Long-term goals: {long_goals}.")
		if self.suggested_path:
			parts.append(f"Suggested path: {self.suggested_path}.")

		# Add any additional info, prioritize `additional_info` answer
		add_info = self.answers.get('additional_info') if isinstance(self.answers, dict) else None
		if add_info:
			parts.append(f"Additional info: {add_info}.")

		return " ".join(parts)

