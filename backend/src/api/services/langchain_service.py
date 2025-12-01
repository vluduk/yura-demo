"""
LangChain-based services for advanced AI features.
Includes multi-step business validation and vector RAG.
"""
import os
import json
from typing import List, Dict, Any, Optional
from django.conf import settings

try:
    from langchain.chains import LLMChain, SequentialChain
    from langchain.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import Document
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_community.vectorstores import Chroma
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class BusinessValidationChain:
    """Multi-step business idea validation using LangChain."""
    
    def __init__(self):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not installed. Run: pip install langchain langchain-google-genai")
        
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        model_name = getattr(settings, 'GOOGLE_LLM_MODEL', 'gemini-2.0-flash-exp')
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
    
    def validate_market(self, business_idea: str) -> str:
        """Step 1: Market Analysis"""
        chain = self._create_market_analysis_chain()
        result = chain.run(business_idea=business_idea)
        return result

    def validate_financials(self, business_idea: str, market_analysis: str) -> str:
        """Step 2: Financial Analysis"""
        chain = self._create_financial_analysis_chain()
        result = chain.run(business_idea=business_idea, market_analysis=market_analysis)
        return result

    def validate_skills(self, business_idea: str, user_context: str) -> str:
        """Step 3: Skills Match"""
        chain = self._create_skills_match_chain()
        result = chain.run(business_idea=business_idea, user_context=user_context)
        return result

    def validate_risks(self, business_idea: str, market_analysis: str, financial_analysis: str, skills_match: str) -> str:
        """Step 4: Risk Assessment"""
        chain = self._create_risk_assessment_chain()
        result = chain.run(
            business_idea=business_idea,
            market_analysis=market_analysis,
            financial_analysis=financial_analysis,
            skills_match=skills_match
        )
        return result

    def validate_verdict(self, business_idea: str, market_analysis: str, financial_analysis: str, skills_match: str, risk_assessment: str) -> str:
        """Step 5: Final Verdict"""
        chain = self._create_final_verdict_chain()
        result = chain.run(
            business_idea=business_idea,
            market_analysis=market_analysis,
            financial_analysis=financial_analysis,
            skills_match=skills_match,
            risk_assessment=risk_assessment
        )
        return result

    def validate_idea(self, business_idea: str, user_context: str) -> Dict[str, Any]:
        """
        Perform multi-step validation of a business idea.
        DEPRECATED: Use individual step methods for interactive validation.
        """
        
        # Step 1: Market Analysis
        market_chain = self._create_market_analysis_chain()
        
        # Step 2: Financial Analysis
        financial_chain = self._create_financial_analysis_chain()
        
        # Step 3: Skills Match
        skills_chain = self._create_skills_match_chain()
        
        # Step 4: Risk Assessment
        risk_chain = self._create_risk_assessment_chain()
        
        # Step 5: Final Verdict
        verdict_chain = self._create_final_verdict_chain()
        
        # Execute sequential chain
        overall_chain = SequentialChain(
            chains=[market_chain, financial_chain, skills_chain, risk_chain, verdict_chain],
            input_variables=["business_idea", "user_context"],
            output_variables=[
                "market_analysis",
                "financial_analysis", 
                "skills_match",
                "risk_assessment",
                "final_verdict"
            ],
            verbose=False
        )
        
        result = overall_chain({
            "business_idea": business_idea,
            "user_context": user_context
        })
        
        return result
    
    def _create_market_analysis_chain(self) -> LLMChain:
        """Chain for market analysis."""
        template = """Проаналізуйте ринкову привабливість бізнес-ідеї.

БІЗНЕС-ІДЕЯ: {business_idea}

ЗАВДАННЯ:
1. Чи існує реальний попит на цей продукт/послугу?
2. Хто цільова аудиторія? (демографія, потреби)
3. Наскільки великий ринок? (потенційні клієнти)
4. Хто основні конкуренти?
5. Яка унікальна цінність пропозиції?

Надайте стислий аналіз (150-200 слів) з КОНКРЕТНИМИ оцінками.

Аналіз ринку:"""
        
        prompt = PromptTemplate(
            input_variables=["business_idea"],
            template=template
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="market_analysis"
        )
    
    def _create_financial_analysis_chain(self) -> LLMChain:
        """Chain for financial viability analysis."""
        template = """На основі попереднього аналізу ринку, оцініть фінансову життєздатність.

БІЗНЕС-ІДЕЯ: {business_idea}
АНАЛІЗ РИНКУ: {market_analysis}

ЗАВДАННЯ:
1. Приблизні початкові витрати (мінімум/максимум)?
2. Постійні щомісячні витрати?
3. Реалістична модель доходів?
4. Коли очікується беззбитковість?
5. Потенційна рентабельність (ROI)?

Надайте КОНКРЕТНІ числа та реалістичні оцінки (150-200 слів).

Фінансовий аналіз:"""
        
        prompt = PromptTemplate(
            input_variables=["business_idea", "market_analysis"],
            template=template
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="financial_analysis"
        )
    
    def _create_skills_match_chain(self) -> LLMChain:
        """Chain for matching user skills to business requirements."""
        template = """Оцініть відповідність навичок користувача вимогам бізнесу.

БІЗНЕС-ІДЕЯ: {business_idea}
ПРОФІЛЬ КОРИСТУВАЧА: {user_context}

ЗАВДАННЯ:
1. Які ключові навички потрібні для цього бізнесу?
2. Які навички є у користувача з профілю?
3. Що ВІДПОВІДАЄ вимогам? (сильні сторони)
4. Які КРИТИЧНІ ПРОГАЛИНИ в навичках?
5. Чи можна заповнити прогалини? Як?

Надайте чесну оцінку відповідності (100-150 слів).

Оцінка навичок:"""
        
        prompt = PromptTemplate(
            input_variables=["business_idea", "user_context"],
            template=template
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="skills_match"
        )
    
    def _create_risk_assessment_chain(self) -> LLMChain:
        """Chain for risk assessment."""
        template = """На основі всіх попередніх аналізів, визначте ключові ризики.

БІЗНЕС-ІДЕЯ: {business_idea}
РИНОК: {market_analysis}
ФІНАНСИ: {financial_analysis}
НАВИЧКИ: {skills_match}

ЗАВДАННЯ:
1. ТОП-3 найбільших ризики для цього бізнесу?
2. Як мітигувати кожен ризик?
3. Які "червоні прапорці" варто враховувати?
4. План Б якщо основна ідея не спрацює?

Надайте практичний аналіз ризиків (150-200 слів).

Оцінка ризиків:"""
        
        prompt = PromptTemplate(
            input_variables=["business_idea", "market_analysis", "financial_analysis", "skills_match"],
            template=template
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="risk_assessment"
        )
    
    def _create_final_verdict_chain(self) -> LLMChain:
        """Chain for final recommendation."""
        template = """На основі ВСІХ попередніх аналізів, надайте фінальний вердикт.

БІЗНЕС-ІДЕЯ: {business_idea}

АНАЛІЗИ:
Ринок: {market_analysis}
Фінанси: {financial_analysis}
Навички: {skills_match}
Ризики: {risk_assessment}

ЗАВДАННЯ:
1. Загальна оцінка ідеї: РЕКОМЕНДУЮ / З ОБЕРЕЖНІСТЮ / НЕ РЕКОМЕНДУЮ
2. Чому саме така оцінка? (2-3 ключові причини)
3. ЩО РОБИТИ ДАЛІ? (конкретні наступні кроки)
4. Альтернативні підходи якщо є сумніви?

Будьте чесними і конструктивними. Якщо ідея слабка, краще сказати це зараз.

Фінальний вердикт:"""
        
        prompt = PromptTemplate(
            input_variables=[
                "business_idea",
                "market_analysis",
                "financial_analysis",
                "skills_match",
                "risk_assessment"
            ],
            template=template
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="final_verdict"
        )
    
    def format_validation_response(self, validation_result: Dict[str, Any]) -> str:
        """Format validation results into a readable response."""
        
        response = f"""📊 ДЕТАЛЬНИЙ АНАЛІЗ БІЗНЕС-ІДЕЇ

🎯 АНАЛІЗ РИНКУ
{validation_result['market_analysis']}

💰 ФІНАНСОВА ОЦІНКА
{validation_result['financial_analysis']}

🛠 ВІДПОВІДНІСТЬ НАВИЧОК
{validation_result['skills_match']}

⚠️ ОЦІНКА РИЗИКІВ
{validation_result['risk_assessment']}

✅ ФІНАЛЬНИЙ ВЕРДИКТ
{validation_result['final_verdict']}
"""
        return response


class VectorRAG:
    """Vector-based Retrieval Augmented Generation for learning mode."""
    
    def __init__(self, persist_directory: str = "/tmp/chroma_db"):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not installed")
        
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        self.persist_directory = persist_directory
        self.vectorstore = None
    
    def initialize_vectorstore(self, force_refresh: bool = False):
        """Initialize or load existing vector store."""
        try:
            if not force_refresh:
                # Try to load existing vectorstore
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            else:
                # Refresh from database
                self._refresh_vectorstore()
        except Exception:
            # Create new if loading fails
            self._refresh_vectorstore()
    
    def _refresh_vectorstore(self):
        """Refresh vectorstore from database."""
        from api.models.knowledge import KnowledgeDocument
        from api.models.article import Article
        
        documents = []
        
        # Load KnowledgeDocuments
        knowledge_docs = KnowledgeDocument.objects.all()
        for doc in knowledge_docs:
            documents.append(Document(
                page_content=doc.raw_text_content,
                metadata={
                    "title": doc.title,
                    "source": doc.source_url or "",
                    "type": "knowledge_document",
                    "id": str(doc.id)
                }
            ))
        
        # Load published Articles
        articles = Article.objects.filter(is_published=True)
        for article in articles:
            documents.append(Document(
                page_content=article.content,
                metadata={
                    "title": article.title,
                    "source": f"/articles/{article.slug}",
                    "type": "article",
                    "id": str(article.id)
                }
            ))
        
        if documents:
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            self.vectorstore.persist()
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant documents.
        
        Returns list of dicts with:
        - title: Document title
        - content: Relevant snippet
        - source: URL or path
        - type: 'knowledge_document' or 'article'
        - relevance_score: Similarity score
        """
        if not self.vectorstore:
            self.initialize_vectorstore()
        
        # Perform similarity search with scores
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            # Extract snippet (first 300 chars)
            content = doc.page_content[:300]
            if len(doc.page_content) > 300:
                content += "..."
            
            formatted_results.append({
                'title': doc.metadata.get('title', 'Untitled'),
                'content': content,
                'source': doc.metadata.get('source', ''),
                'type': doc.metadata.get('type', 'unknown'),
                'relevance_score': float(1 - score)  # Convert distance to similarity
            })
        
        return formatted_results
    
    def format_rag_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM context."""
        if not results:
            return ""
        
        context = "\n\nРЕЛЕВАНТНІ МАТЕРІАЛИ З БАЗИ ЗНАНЬ:\n"
        for i, result in enumerate(results, 1):
            context += f"\n{i}. [{result['type'].upper()}] {result['title']}\n"
            context += f"   {result['content']}\n"
            if result['source']:
                context += f"   Джерело: {result['source']}\n"
            context += f"   Релевантність: {result['relevance_score']:.2%}\n"
        
        return context
