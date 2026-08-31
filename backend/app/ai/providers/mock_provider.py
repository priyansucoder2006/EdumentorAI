import json
from typing import Type, TypeVar, Optional, Dict, Any, List
from pydantic import BaseModel
from app.ai.providers.base import BaseLLMProvider
from app.schemas.lesson import LessonPlanLLMOutput, LessonStepLLMOutput, QuestionSchema
from app.schemas.interaction import AnswerEvaluationResult, MisconceptionResult
from app.schemas.assessment import AssessmentLLMOutput, AssessmentQuestionItem
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class MockPedagogicalProvider(BaseLLMProvider):
    """
    Production-grade deterministic educational provider for offline development,
    demonstrations, and automated test scenarios.
    Provides comprehensive subject-aware pedagogical responses for physics, CS, math, biology, etc.
    """

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        prompt_lower = prompt.lower()
        if "translate" in prompt_lower or "hinglish" in prompt_lower:
            return "Chaliye ab hum agla concept detail mein samajhte hain!"
        return "Let's explore this concept step by step."

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> T:
        prompt_lower = prompt.lower()

        # 1. Lesson Planning
        if response_schema == LessonPlanLLMOutput:
            plan_dict = self._generate_mock_lesson_plan(prompt, prompt_lower)
            return response_schema.model_validate(plan_dict)

        # 2. Answer Evaluation
        if response_schema == AnswerEvaluationResult:
            eval_dict = self._evaluate_mock_answer(prompt, prompt_lower)
            return response_schema.model_validate(eval_dict)

        # 3. Misconception Detection
        if response_schema == MisconceptionResult:
            misc_dict = self._diagnose_mock_misconception(prompt, prompt_lower)
            return response_schema.model_validate(misc_dict)

        # 4. Assessment Generation
        if response_schema == AssessmentLLMOutput:
            assess_dict = self._generate_mock_assessment(prompt, prompt_lower)
            return response_schema.model_validate(assess_dict)

        # Fallback default instantiation
        try:
            return response_schema()
        except Exception:
            raise ValueError(f"MockProvider cannot satisfy schema: {response_schema}")

    def _generate_mock_lesson_plan(self, prompt: str, prompt_lower: str) -> Dict[str, Any]:
        duration = 20
        if "5 minute" in prompt_lower or "duration: 5" in prompt_lower:
            duration = 5
        elif "60 minute" in prompt_lower or "duration: 60" in prompt_lower:
            duration = 60

        lang = "en"
        if "hinglish" in prompt_lower:
            lang = "hinglish"
        elif "hindi" in prompt_lower:
            lang = "hi"
        elif "bengali" in prompt_lower or "bn" in prompt_lower:
            lang = "bn"

        # Topic: Newton's Laws (Flagship Demonstration & Test Scenario)
        if "newton" in prompt_lower or "force" in prompt_lower or "motion" in prompt_lower:
            return self._build_newtons_laws_plan(duration, lang)
        
        # Topic: React / Web Development
        if "react" in prompt_lower or "frontend" in prompt_lower or "component" in prompt_lower:
            return self._build_react_plan(duration, lang)

        # Topic: Ohm's Law / Electricity
        if "ohm" in prompt_lower or "circuit" in prompt_lower or "electricity" in prompt_lower:
            return self._build_ohms_law_plan(duration, lang)

        # Topic: Machine Learning / AI
        if "machine learning" in prompt_lower or "artificial intelligence" in prompt_lower or "ai" in prompt_lower:
            return self._build_ml_plan(duration, lang)

        # Generic Subject Plan
        return self._build_generic_plan(prompt, duration, lang)

    def _build_newtons_laws_plan(self, duration: int, lang: str) -> Dict[str, Any]:
        if lang == "hinglish":
            summary = "Newton's Laws of Motion ko intuitively real-world examples aur visuals ke saath samajhna."
            s1_exp = "Newton ka First Law (Law of Inertia) kehta hai ki koi object rest pe rahega, ya constant speed se straight line mein move karta rahega, jab tak koi external unbalanced force na lage."
            s1_analogy = "Socho aap ek frictionless ice rink par hockey puck ko slide karte ho. Agar koi friction ya hawa na ho, toh puck kabhi nahi rukegi!"
            s1_q = "Agar ek car achanak brake lagaye, toh passenger aage ki taraf kyu jhukta hai?"
            s1_opts = [
                "Inertia of motion ki wajah se passenger ki body aage move karti rehna chahti hai.",
                "Car unhe aage ki taraf dhakka deti hai.",
                "Gravity badh jati hai jab brake lagti hai.",
                "Friction unhe aage kheenchti hai."
            ]
            s2_exp = "Newton ka Second Law relationship batata hai: Force = Mass × Acceleration ($F = ma$). Jitna zyada mass hoga, use accelerate karne ke liye utna zyada force chahiye."
            s2_analogy = "Ek choti bicycle ko push karna asaan hai, par ek heavy truck ko accelerate karne ke liye bohot powerful engine ka force chahiye hota hai."
            s2_q = "Agar mass constant rahe aur Force ko double kar diya jaye, toh acceleration par kya asar hoga?"
            s2_opts = ["Acceleration bhi double ho jayegi", "Acceleration aadhi ho jayegi", "Acceleration same rahegi", "Acceleration zero ho jayegi"]
            s3_exp = "Newton ka Third Law kehta hai: Har action ka ek equal aur opposite reaction hota hai ($F_{AB} = -F_{BA}$). Forces hamesha pairs mein exist karte hain."
            s3_analogy = "Jab rocket exhaust gases ko bohot tezi se neeche push karta hai (Action), tab gases rocket ko utne hi force se upar push karti hain (Reaction)."
            s3_q = "Jab aap swimming karte hue paani ko peeche dhakelte ho, toh aap aage kyu badhte ho?"
            s3_opts = ["Paani aapko equal aur opposite force se aage dhakelta hai", "Paani ka weight kam ho jata hai", "Gravity disappear ho jati hai", "Friction zero ho jati hai"]
        else:
            summary = "Master Newton's Three Laws of Motion with real-world physics intuition, mathematics, and free-body diagrams."
            s1_exp = "Newton's First Law (Law of Inertia) states that an object at rest stays at rest, and an object in uniform motion stays in motion along a straight line, unless acted upon by an unbalanced external force."
            s1_analogy = "Imagine sliding a hockey puck on an endless sheet of perfectly frictionless ice. Without friction or air resistance, it will glide forever at constant velocity."
            s1_q = "Why does a passenger lurch forward when a moving bus suddenly hits the brakes?"
            s1_opts = [
                "Because of inertia of motion, the passenger's body continues moving forward.",
                "A mysterious forward force pushes the passenger.",
                "Gravity pulls the passenger forward during braking.",
                "Friction between tires and road creates a forward pull on the passenger."
            ]
            s2_exp = "Newton's Second Law establishes the fundamental formula: Force = Mass × Acceleration ($F = ma$). The acceleration of an object is directly proportional to the net force and inversely proportional to its mass."
            s2_analogy = "Pushing an empty shopping cart requires very little force to accelerate quickly, while pushing a cart filled with bricks requires significant effort."
            s2_q = "If the net force acting on an object is doubled while its mass remains constant, what happens to its acceleration?"
            s2_opts = ["Acceleration doubles", "Acceleration is halved", "Acceleration remains unchanged", "Acceleration drops to zero"]
            s3_exp = "Newton's Third Law states: For every action, there is an equal and opposite reaction ($F_{A \\to B} = -F_{B \\to A}$). Forces always occur in matched pairs acting on different objects."
            s3_analogy = "When a rocket engine violently expels combustion gases downward (Action), the gases exert an equal upward thrust propelling the rocket into space (Reaction)."
            s3_q = "When a swimmer pushes water backward with their hands, what causes them to move forward?"
            s3_opts = ["The water exerts an equal and opposite forward force on the swimmer", "The water becomes lighter", "Gravity temporarily decreases", "Buoyancy turns into kinetic propulsion"]

        steps = [
            LessonStepLLMOutput(
                step_number=1,
                concept="First Law: Inertia & Net Force",
                explanation=s1_exp,
                example="A coin placed on a card over a glass drops directly into the glass when the card is flicked away horizontally.",
                analogy=s1_analogy,
                visual_type="physics_sim",
                visual_data={
                    "type": "physics_sim",
                    "title": "Newton's First Law: Inertia on Frictionless Surface",
                    "data": {
                        "object_name": "Glider on Air Track",
                        "mass_kg": 2.0,
                        "velocity_mps": 5.0,
                        "net_force_N": 0.0,
                        "state": "Uniform Linear Motion",
                        "formula": "F_{net} = 0 \\implies a = 0, v = \\text{constant}"
                    },
                    "caption": "When net force is zero, velocity remains strictly constant indefinitely."
                },
                question=QuestionSchema(
                    id="q_newton_1",
                    type="mcq",
                    prompt=s1_q,
                    options=s1_opts,
                    correct_answer=s1_opts[0],
                    explanation_guide="Inertia is the inherent resistance of any physical object to any change in its velocity.",
                    difficulty="beginner"
                ),
                expected_answer="Inertia of motion causes the passenger's body to resist the sudden deceleration.",
                difficulty="beginner"
            )
        ]

        if duration >= 20:
            steps.append(
                LessonStepLLMOutput(
                    step_number=2,
                    concept="Second Law: F = ma & Momentum Rate",
                    explanation=s2_exp,
                    example="A 1000 kg car accelerating at 2 m/s² requires a net forward force of F = 1000 × 2 = 2000 N.",
                    analogy=s2_analogy,
                    visual_type="math",
                    visual_data={
                        "type": "math",
                        "title": "Mathematical Derivation of Newton's 2nd Law",
                        "data": {
                            "equation": "F_{net} = \\frac{dp}{dt} = m \\cdot \\frac{dv}{dt} = m \\cdot a",
                            "steps": [
                                "1. Momentum: p = m \\cdot v",
                                "2. Rate of change of momentum: \\frac{dp}{dt} = m \\frac{dv}{dt} (for constant mass)",
                                "3. Since acceleration a = \\frac{dv}{dt}, we arrive at F = m \\cdot a",
                                "4. SI Units: 1 \\text{ Newton (N)} = 1 \\text{ kg} \\cdot \\text{m/s}^2"
                            ]
                        },
                        "caption": "Force produces acceleration inversely proportional to mass."
                    },
                    question=QuestionSchema(
                        id="q_newton_2",
                        type="mcq",
                        prompt=s2_q,
                        options=s2_opts,
                        correct_answer=s2_opts[0],
                        explanation_guide="According to F = ma, acceleration a = F/m. If F doubles and m is constant, a doubles.",
                        difficulty="intermediate"
                    ),
                    expected_answer="The acceleration doubles proportionally.",
                    difficulty="intermediate"
                )
            )

        if duration >= 60:
            steps.append(
                LessonStepLLMOutput(
                    step_number=3,
                    concept="Third Law: Action-Reaction Force Pairs",
                    explanation=s3_exp,
                    example="A cannon recoils backward when firing a heavy cannonball forward.",
                    analogy=s3_analogy,
                    visual_type="diagram",
                    visual_data={
                        "type": "diagram",
                        "title": "Action-Reaction Pair Diagram",
                        "data": {
                            "mermaid": "graph LR\n  Rocket[Rocket Body] -- Action: Gas expelled downward --> Exhaust[High-Speed Exhaust Gas]\n  Exhaust -- Reaction: Upward thrust on rocket --> Rocket",
                            "force_action": "F_action = -F_reaction",
                            "key_rule": "Forces act on two DIFFERENT interacting bodies"
                        },
                        "caption": "Action and reaction forces never cancel each other out because they act on separate bodies."
                    },
                    question=QuestionSchema(
                        id="q_newton_3",
                        type="mcq",
                        prompt=s3_q,
                        options=s3_opts,
                        correct_answer=s3_opts[0],
                        explanation_guide="The backward push against water generates an equal forward reaction push on the swimmer.",
                        difficulty="intermediate"
                    ),
                    expected_answer="The water exerts an equal and opposite reaction force pushing the swimmer forward.",
                    difficulty="intermediate"
                )
            )

        return {
            "topic": "Newton's Laws of Motion",
            "duration_minutes": duration,
            "language": lang,
            "difficulty": "beginner",
            "objectives": [
                "Understand the principle of Inertia and balanced forces",
                "Apply the mathematical relationship F = ma to calculate force and acceleration",
                "Identify Action-Reaction force pairs across diverse real-world systems"
            ],
            "prerequisites": ["Basic understanding of speed, velocity, and pushing/pulling forces"],
            "summary": summary,
            "steps": [s.model_dump() for s in steps]
        }

    def _build_react_plan(self, duration: int, lang: str) -> Dict[str, Any]:
        return {
            "topic": "React Components & State Management",
            "duration_minutes": duration,
            "language": lang,
            "difficulty": "intermediate",
            "objectives": [
                "Understand the declarative component lifecycle",
                "Master useState and unidirectional data flow",
                "Avoid common anti-patterns like direct state mutation"
            ],
            "prerequisites": ["JavaScript ES6 Fundamentals, Arrow Functions, Destructuring"],
            "summary": "Master modern React architecture with live code execution simulation and reactive UI principles.",
            "steps": [
                {
                    "step_number": 1,
                    "concept": "Components & Props as Pure Functions",
                    "explanation": "In React, a component is essentially a JavaScript function that accepts 'props' as input and returns JSX describing what the UI should look like.",
                    "example": "function Greeting({ name }) { return <h1>Hello, {name}!</h1>; }",
                    "analogy": "Think of a component like a blueprint or a cookie cutter: you define the shape once, and pass different ingredients (props) to create unique cookies.",
                    "visual_type": "code",
                    "visual_data": {
                        "type": "code",
                        "title": "Pure React Component",
                        "data": {
                            "language": "typescript",
                            "code": "interface UserCardProps {\n  name: string;\n  role: string;\n}\n\nexport const UserCard: React.FC<UserCardProps> = ({ name, role }) => {\n  return (\n    <div className=\"card\">\n      <h3>{name}</h3>\n      <span className=\"badge\">{role}</span>\n    </div>\n  );\n};",
                            "output": "Rendered: <div class='card'><h3>Alex</h3><span class='badge'>Engineer</span></div>"
                        }
                    },
                    "question": {
                        "id": "q_react_1",
                        "type": "mcq",
                        "prompt": "Can a child component directly modify the props it receives from its parent?",
                        "options": [
                            "No, props are read-only (immutable) in React.",
                            "Yes, props can be reassigned freely like local variables.",
                            "Only if the prop is a string or number.",
                            "Yes, by using the this.props.set() method."
                        ],
                        "correct_answer": "No, props are read-only (immutable) in React.",
                        "difficulty": "beginner"
                    },
                    "expected_answer": "Props are strictly read-only and immutable.",
                    "difficulty": "beginner"
                }
            ]
        }

    def _build_ohms_law_plan(self, duration: int, lang: str) -> Dict[str, Any]:
        return {
            "topic": "Ohm's Law & Electric Circuits",
            "duration_minutes": duration,
            "language": lang,
            "difficulty": "beginner",
            "objectives": ["Relate Voltage, Current, and Resistance via V = IR"],
            "prerequisites": ["Basic charge and potential concept"],
            "summary": "Understand how electric current flows through conductors using the water pipe analogy.",
            "steps": [
                {
                    "step_number": 1,
                    "concept": "Ohm's Law: V = IR",
                    "explanation": "Ohm's Law states that electric current (I) is directly proportional to voltage (V) and inversely proportional to resistance (R).",
                    "example": "If a 12V battery is connected across a 4 ohm resistor, the current is I = 12 / 4 = 3 Amperes.",
                    "analogy": "Imagine a water pipe: Voltage is the water pressure pump, Current is the volume of water flowing per second, and Resistance is a narrow constriction in the pipe.",
                    "visual_type": "math",
                    "visual_data": {
                        "type": "math",
                        "title": "Ohm's Law Formula Triangle",
                        "data": {
                            "equation": "V = I \\times R \\iff I = \\frac{V}{R} \\iff R = \\frac{V}{I}",
                            "steps": [
                                "V: Voltage in Volts (V)",
                                "I: Current in Amperes (A)",
                                "R: Resistance in Ohms (\\Omega)"
                            ]
                        }
                    },
                    "question": {
                        "id": "q_ohm_1",
                        "type": "mcq",
                        "prompt": "If resistance in a circuit increases while voltage stays constant, what happens to current?",
                        "options": [
                            "Current decreases proportionally.",
                            "Current increases because resistance creates more power.",
                            "Current remains completely constant.",
                            "Voltage automatically doubles."
                        ],
                        "correct_answer": "Current decreases proportionally.",
                        "difficulty": "beginner"
                    },
                    "expected_answer": "Current decreases because resistance opposes electric flow.",
                    "difficulty": "beginner"
                }
            ]
        }

    def _build_ml_plan(self, duration: int, lang: str) -> Dict[str, Any]:
        return {
            "topic": "Machine Learning Fundamentals",
            "duration_minutes": duration,
            "language": lang,
            "difficulty": "beginner",
            "objectives": ["Distinguish Supervised vs Unsupervised learning", "Understand Training vs Inference"],
            "prerequisites": ["Basic data concepts"],
            "summary": "Explore how machines learn patterns from data rather than following hardcoded rules.",
            "steps": [
                {
                    "step_number": 1,
                    "concept": "Supervised Learning: Learning from Labeled Data",
                    "explanation": "Supervised learning algorithms are trained on input-output pairs. The algorithm learns a mathematical mapping function $y = f(x)$ that predicts labels for new unseen inputs.",
                    "example": "Spam filtering: Input email text ($x$) -> Output label ($y$: Spam or Not Spam).",
                    "analogy": "Like a student practicing math problems with an answer key at the back of the book to check their mistakes.",
                    "visual_type": "diagram",
                    "visual_data": {
                        "type": "diagram",
                        "title": "Supervised Learning Pipeline",
                        "data": {
                            "mermaid": "graph LR\n  Data[Features X + Labels Y] --> Model[Training Algorithm]\n  Model --> Predictor[Trained Model f(x)]\n  NewX[New Input X] --> Predictor\n  Predictor --> Output[Prediction Y_hat]"
                        }
                    },
                    "question": {
                        "id": "q_ml_1",
                        "type": "mcq",
                        "prompt": "Which of the following is a classic example of supervised learning?",
                        "options": [
                            "House price prediction based on historical sold prices and features.",
                            "Clustering customers into unknown purchasing personas without labels.",
                            "Dimensionality reduction using PCA.",
                            "Compressing raw video files without metadata."
                        ],
                        "correct_answer": "House price prediction based on historical sold prices and features.",
                        "difficulty": "beginner"
                    },
                    "expected_answer": "Predicting house prices using labeled historical sales data.",
                    "difficulty": "beginner"
                }
            ]
        }

    def _build_generic_plan(self, prompt: str, duration: int, lang: str) -> Dict[str, Any]:
        topic = "Fundamental Principles"
        for line in prompt.split("\n"):
            if line.lower().startswith("topic:"):
                topic = line.split(":", 1)[1].strip()
                break

        return {
            "topic": topic,
            "duration_minutes": duration,
            "language": lang,
            "difficulty": "beginner",
            "objectives": [f"Understand core concepts of {topic}", "Apply principles to solve concrete questions"],
            "prerequisites": ["Basic foundational literacy in the subject"],
            "summary": f"A comprehensive, structured lesson on {topic}.",
            "steps": [
                {
                    "step_number": 1,
                    "concept": f"Introduction to {topic}",
                    "explanation": f"In this module, we break down {topic} into intuitive building blocks.",
                    "example": f"Real-world application of {topic} in modern science and industry.",
                    "analogy": f"Think of {topic} as a foundational pillar upon which advanced systems are constructed.",
                    "visual_type": "diagram",
                    "visual_data": {
                        "type": "diagram",
                        "title": f"Core Structure of {topic}",
                        "data": {
                            "mermaid": f"graph TD\n  Root[{topic}] --> Foundations[Foundations]\n  Root --> Applications[Applications]"
                        }
                    },
                    "question": {
                        "id": "q_gen_1",
                        "type": "mcq",
                        "prompt": f"What is the primary objective when studying {topic}?",
                        "options": [
                            "To understand the fundamental principles and apply them effectively.",
                            "To memorize arbitrary terms without conceptual understanding.",
                            "To avoid practical examples completely.",
                            "To treat all formulas as decorative text."
                        ],
                        "correct_answer": "To understand the fundamental principles and apply them effectively.",
                        "difficulty": "beginner"
                    },
                    "expected_answer": "Understanding core principles and practical application.",
                    "difficulty": "beginner"
                }
            ]
        }

    def _evaluate_mock_answer(self, prompt: str, prompt_lower: str) -> Dict[str, Any]:
        # Detect student answers indicating misconceptions or wrong ideas
        is_wrong = False
        feedback = "Excellent! You explained the core concept clearly and accurately."
        score = 1.0
        missing = []
        reasoning = "excellent"

        wrong_keywords = [
            "heavier falls faster",
            "heavier object falls faster",
            "force is needed to keep moving",
            "force keeps motion",
            "friction pulls forward",
            "gravity increases when braking",
            "car pushes them",
            "current is consumed",
            "voltage consumed",
            "current increases with resistance",
            "props can be modified",
            "directly mutate"
        ]

        if any(kw in prompt_lower for kw in wrong_keywords) or "option 2" in prompt_lower or "option 3" in prompt_lower or "incorrect" in prompt_lower:
            is_wrong = True
            score = 0.25
            feedback = "Not quite. There is a common misconception in your reasoning regarding how forces and motion interact."
            missing = ["Inertia of motion", "Frictional forces vs inherent momentum"]
            reasoning = "poor"

        return {
            "is_correct": not is_wrong,
            "score": score,
            "confidence": 0.95,
            "feedback": feedback,
            "missing_concepts": missing,
            "reasoning_quality": reasoning
        }

    def _diagnose_mock_misconception(self, prompt: str, prompt_lower: str) -> Dict[str, Any]:
        root_cause = "Student believes force is necessary to maintain velocity, confusing friction with the intrinsic nature of motion."
        title = "Aristotelian Motion Fallacy vs. Newtonian Inertia"
        analogy = "Imagine sliding a hockey puck on frictionless ice in deep space. Once you give it a push, it glides forever without needing any continuous push!"
        strategy = "Use frictionless thought experiments and contrast with friction-dominated everyday environments."
        severity = "medium"

        if "current" in prompt_lower or "resistance" in prompt_lower:
            root_cause = "Student believes electric current gets used up or increases when opposition increases."
            title = "Current Flow vs. Resistance Inversion"
            analogy = "Think of a water pipe: making the pipe narrower (higher resistance) restricts the water flow, so LESS water comes out per second."
            strategy = "Water pipe constriction visual demonstration."
        elif "heavier" in prompt_lower or "fall" in prompt_lower:
            root_cause = "Student believes gravitational acceleration depends on object mass, ignoring that all objects accelerate at g in a vacuum."
            title = "Mass-Independence of Gravitational Acceleration"
            analogy = "In Apollo 15's famous Moon experiment, astronaut David Scott dropped a heavy hammer and a light falcon feather simultaneously in the lunar vacuum; both hit the ground at the exact same instant!"
            strategy = "Vacuum drop thought experiment."

        return {
            "detected": True,
            "root_cause": root_cause,
            "misconception_title": title,
            "severity": severity,
            "pedagogical_analogy": analogy,
            "recommended_reteach_strategy": strategy
        }

    def _generate_mock_assessment(self, prompt: str, prompt_lower: str) -> Dict[str, Any]:
        return {
            "title": "Comprehensive Mastery Assessment",
            "questions": [
                {
                    "id": "aq1",
                    "concept": "Inertia and First Law",
                    "difficulty": "beginner",
                    "type": "mcq",
                    "prompt": "If a space probe is traveling at 10,000 km/h in deep interstellar space far from any star or planet, how much rocket thrust is needed to keep it traveling at this speed?",
                    "options": [
                        "Zero thrust (0 N), because no external force is acting to slow it down.",
                        "Continuous 10,000 N thrust.",
                        "Thrust proportional to the mass of the probe.",
                        "Constant thrust to overcome cosmic inertia."
                    ],
                    "correct_answer": "Zero thrust (0 N), because no external force is acting to slow it down.",
                    "explanation": "According to Newton's First Law, an object in motion stays in motion at constant velocity when net external force is zero."
                },
                {
                    "id": "aq2",
                    "concept": "Second Law F = ma",
                    "difficulty": "intermediate",
                    "type": "mcq",
                    "prompt": "A 5 kg mass is accelerated at 4 m/s². What net force was applied to the mass?",
                    "options": [
                        "20 N",
                        "1.25 N",
                        "0.8 N",
                        "9 N"
                    ],
                    "correct_answer": "20 N",
                    "explanation": "Using F = ma: F = 5 kg × 4 m/s² = 20 N."
                },
                {
                    "id": "aq3",
                    "concept": "Third Law Action-Reaction",
                    "difficulty": "intermediate",
                    "type": "mcq",
                    "prompt": "Why don't action and reaction force pairs cancel each other out?",
                    "options": [
                        "Because they act on two different interacting objects, not the same object.",
                        "Because action force is always slightly larger than reaction force.",
                        "Because they occur at different times.",
                        "Because reaction force exists only in fluids."
                    ],
                    "correct_answer": "Because they act on two different interacting objects, not the same object.",
                    "explanation": "Newton's Third Law force pairs act on separate objects, so they do not cancel in a single object's free-body diagram."
                }
            ]
        }
