"""
Phase 3: Memory & Feedback System Implementation

This module implements structured long-term memory using vector databases
and preference data collection for fine-tuning the core model.

Key features:
1. Structured experience logging (JSON format)
2. Vector database integration (ChromaDB) for semantic memory retrieval
3. Human feedback interface for preference data collection
4. Experience-based learning and task similarity detection
"""

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

try:
    import pinecone  # type: ignore[import-not-found] # noqa: F401
    HAS_PINECONE = False  # Pinecone requires API key, disabled for now
except ImportError:
    HAS_PINECONE = False

import logging

logger = logging.getLogger(__name__)


@dataclass
class TaskExperience:
    """Structured representation of a task solving experience."""
    task_id: str
    task_name: str
    task_description: str
    agent_type: str
    timestamp: float
    steps: List[Dict[str, Any]]
    final_success: bool
    final_code: str
    test_results: str
    performance_metrics: Dict[str, float]
    human_feedback: Optional[Dict[str, Any]] = None
    improvement_suggestions: List[str] = field(default_factory=list)


@dataclass
class PreferencePair:
    """Preference pair for DPO training."""
    task_id: str
    task_description: str
    chosen_solution: str
    rejected_solution: str
    chosen_reasoning: str
    rejected_reasoning: str
    preference_score: float  # 0-1, higher = stronger preference
    human_feedback: Optional[str] = None
    timestamp: float = field(default_factory=lambda: time.time())


class StructuredLogger:
    """Converts raw memory.txt logs into structured JSON format."""

    def __init__(self, memory_file: str = "memory.txt", structured_file: str = "structured_memory.json"):
        self.memory_file = Path(memory_file)
        self.structured_file = Path(structured_file)
        self.experiences: List[TaskExperience] = []

        # Load existing structured data if available
        if self.structured_file.exists():
            self._load_structured_data()

    def _load_structured_data(self) -> None:
        """Load existing structured memory data."""
        try:
            with open(self.structured_file) as f:
                data = json.load(f)
                self.experiences = [TaskExperience(**exp) for exp in data]
            logger.info(f"Loaded {len(self.experiences)} existing experiences")
        except Exception as e:
            logger.warning(f"Could not load structured data: {e}")
            self.experiences = []

    def parse_memory_file(self) -> List[TaskExperience]:
        """Parse raw memory.txt file into structured experiences."""
        if not self.memory_file.exists():
            logger.warning("Memory file not found")
            return []

        try:
            with open(self.memory_file) as f:
                content = f.read()

            # Split by session completion markers
            sessions = content.split('SESSION COMPLETE:')
            parsed_experiences = []

            for session in sessions[1:]:  # Skip empty first part
                experience = self._parse_session(session)
                if experience:
                    parsed_experiences.append(experience)

            # Merge with existing experiences (avoid duplicates)
            new_experiences = []
            existing_ids = {exp.task_id for exp in self.experiences}

            for exp in parsed_experiences:
                if exp.task_id not in existing_ids:
                    new_experiences.append(exp)
                    self.experiences.append(exp)

            logger.info(f"Parsed {len(new_experiences)} new experiences")
            self._save_structured_data()

            return self.experiences

        except Exception as e:
            logger.error(f"Error parsing memory file: {e}")
            return self.experiences

    def _parse_session(self, session_text: str) -> Optional[TaskExperience]:
        """Parse a single session from memory.txt."""
        try:
            lines = session_text.strip().split('\n')

            # Extract session info
            task_name = None
            final_success = False
            total_steps = 0
            duration = 0.0

            for line in lines:
                if line.strip().startswith('SESSION COMPLETE:'):
                    continue
                elif 'Final Success:' in line:
                    final_success = 'True' in line
                elif 'Total Steps:' in line:
                    total_steps = int(line.split(':')[1].strip())
                elif 'Duration:' in line:
                    duration = float(line.split(':')[1].strip().rstrip('s'))

            # Find steps by looking backwards in memory file
            steps = self._extract_steps_for_session(session_text)

            # Generate task ID and extract task name from steps
            if steps:
                task_name = self._extract_task_name_from_steps(steps)

            if not task_name:
                return None

            task_id = str(uuid.uuid4())

            return TaskExperience(
                task_id=task_id,
                task_name=task_name,
                task_description=f"Task: {task_name}",
                agent_type="ReAct-Enhanced",
                timestamp=time.time(),
                steps=steps,
                final_success=final_success,
                final_code=self._extract_final_code_from_steps(steps),
                test_results=self._extract_test_results_from_steps(steps),
                performance_metrics={
                    "duration": duration,
                    "total_steps": total_steps,
                    "success_rate": 1.0 if final_success else 0.0
                }
            )

        except Exception as e:
            logger.error(f"Error parsing session: {e}")
            return None

    def _extract_steps_for_session(self, session_text: str) -> List[Dict[str, Any]]:
        """Extract individual steps from session text."""
        # This is simplified - in practice would parse the step-by-step logs
        # For now, create a summary step
        steps = []

        if "THOUGHT:" in session_text:
            # Basic parsing for demonstration
            step = {
                "step_number": 1,
                "thought": "Session completed",
                "action": "complete_task",
                "observation": "Task finished",
                "success": "True" in session_text
            }
            steps.append(step)

        return steps

    def _extract_task_name_from_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Extract task name from steps."""
        # Look for task names in thoughts/actions
        for step in steps:
            if "Stock" in str(step):
                return "Stock Price Fetcher"
            elif "File" in str(step):
                return "File Organizer"
            elif "Text" in str(step):
                return "Text Processor"
        return "Unknown Task"

    def _extract_final_code_from_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Extract final successful code from steps."""
        # Simplified - would extract actual code from successful steps
        return "# Final code would be extracted from successful execution steps"

    def _extract_test_results_from_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Extract test results from steps."""
        return json.dumps({"test_status": "completed", "success": True})

    def _save_structured_data(self) -> None:
        """Save structured experiences to JSON file."""
        try:
            with open(self.structured_file, 'w') as f:
                json.dump([asdict(exp) for exp in self.experiences], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving structured data: {e}")


class VectorMemoryStore:
    """Vector database for semantic memory retrieval."""

    def __init__(self, db_path: str = "./chroma_memory", collection_name: str = "task_experiences"):
        self.db_path = db_path
        self.collection_name = collection_name
        self.client: Optional[Any] = None
        self.collection: Optional[Any] = None

        if HAS_CHROMADB:
            self._initialize_chromadb()
        else:
            logger.warning("ChromaDB not available - falling back to simple memory")

    def _initialize_chromadb(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)

            # Get or create collection
            try:
                if self.client:
                    self.collection = self.client.get_collection(name=self.collection_name)
                    logger.info(f"Loaded existing collection: {self.collection_name}")
            except Exception:
                if self.client:
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        metadata={"description": "Task solving experiences for semantic retrieval"}
                    )
                    logger.info(f"Created new collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            self.client = None
            self.collection = None

    def add_experience(self, experience: TaskExperience) -> None:
        """Add an experience to the vector store."""
        if not self.collection:
            return

        try:
            # Create searchable text from experience
            searchable_text = self._create_searchable_text(experience)

            # Add to collection
            self.collection.add(
                documents=[searchable_text],
                metadatas=[{
                    "task_id": experience.task_id,
                    "task_name": experience.task_name,
                    "success": experience.final_success,
                    "agent_type": experience.agent_type,
                    "timestamp": experience.timestamp
                }],
                ids=[experience.task_id]
            )

            logger.debug(f"Added experience {experience.task_id} to vector store")

        except Exception as e:
            logger.error(f"Error adding experience to vector store: {e}")

    def find_similar_experiences(self, task_description: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar past experiences for a given task."""
        if not self.collection:
            return []

        try:
            results = self.collection.query(
                query_texts=[task_description],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )

            similar_experiences = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    similar_experiences.append({
                        "document": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "similarity": 1.0 - results['distances'][0][i] if results['distances'] else 0.0
                    })

            logger.info(f"Found {len(similar_experiences)} similar experiences")
            return similar_experiences

        except Exception as e:
            logger.error(f"Error finding similar experiences: {e}")
            return []

    def _create_searchable_text(self, experience: TaskExperience) -> str:
        """Create searchable text representation of an experience."""
        text_parts = [
            f"Task: {experience.task_name}",
            f"Description: {experience.task_description}",
            f"Success: {experience.final_success}",
            f"Agent: {experience.agent_type}"
        ]

        # Add step summaries
        for step in experience.steps:
            if step.get('thought'):
                text_parts.append(f"Thought: {step['thought']}")
            if step.get('action'):
                text_parts.append(f"Action: {step['action']}")

        return " | ".join(text_parts)


class HumanFeedbackInterface:
    """Interface for collecting human feedback on agent solutions."""

    def __init__(self, feedback_file: str = "human_feedback.json"):
        self.feedback_file = Path(feedback_file)
        self.feedback_data: List[Dict[str, Any]] = []

        # Load existing feedback
        if self.feedback_file.exists():
            self._load_feedback()

    def _load_feedback(self) -> None:
        """Load existing feedback data."""
        try:
            with open(self.feedback_file) as f:
                self.feedback_data = json.load(f)
            logger.info(f"Loaded {len(self.feedback_data)} feedback entries")
        except Exception as e:
            logger.warning(f"Could not load feedback data: {e}")
            self.feedback_data = []

    def collect_feedback(self, experience: TaskExperience, interactive: bool = False) -> Dict[str, Any]:
        """Collect human feedback on a task experience."""
        if interactive:
            return self._interactive_feedback(experience)
        else:
            return self._automated_feedback(experience)

    def _interactive_feedback(self, experience: TaskExperience) -> Dict[str, Any]:
        """Collect feedback interactively via CLI."""
        print(f"\n{'='*60}")
        print(f"FEEDBACK REQUEST: {experience.task_name}")
        print(f"{'='*60}")
        print(f"Task: {experience.task_name}")
        print(f"Success: {experience.final_success}")
        print(f"Steps: {len(experience.steps)}")
        print(f"Duration: {experience.performance_metrics.get('duration', 0):.2f}s")
        print("\nFinal Code Preview:")
        print("-" * 40)
        print(experience.final_code[:300] + "..." if len(experience.final_code) > 300 else experience.final_code)
        print("-" * 40)

        # Collect feedback
        feedback = {}

        # Quality rating
        while True:
            try:
                quality_str = input("\nRate solution quality (1-5, 5=excellent): ").strip()
                quality = int(quality_str)
                if 1 <= quality <= 5:
                    feedback['quality'] = quality
                    break
                else:
                    print("Please enter a number between 1 and 5")
            except ValueError:
                print("Please enter a valid number")

        # Correctness
        while True:
            correct = input("Is the solution correct? (y/n): ").strip().lower()
            if correct in ['y', 'yes']:
                feedback['correct'] = True
                break
            elif correct in ['n', 'no']:
                feedback['correct'] = False
                break
            else:
                print("Please enter 'y' or 'n'")

        # Efficiency
        while True:
            try:
                efficiency_str = input("Rate solution efficiency (1-5, 5=very efficient): ").strip()
                efficiency = int(efficiency_str)
                if 1 <= efficiency <= 5:
                    feedback['efficiency'] = efficiency
                    break
                else:
                    print("Please enter a number between 1 and 5")
            except ValueError:
                print("Please enter a valid number")

        # Comments
        comments = input("Additional comments (optional): ").strip()
        if comments:
            feedback['comments'] = comments  # type: ignore[assignment]

        # Overall preference (for DPO training)
        quality_score = int(feedback['quality'])
        efficiency_score = int(feedback['efficiency'])
        overall_score = (quality_score + efficiency_score) / 2
        if feedback['correct']:
            overall_score += 1  # Bonus for correctness

        feedback['overall_score'] = min(overall_score / 6, 1.0)  # type: ignore[assignment]
        feedback['timestamp'] = time.time()  # type: ignore[assignment]
        feedback['task_id'] = str(experience.task_id)  # type: ignore[assignment]

        # Save feedback
        self.feedback_data.append(feedback)
        self._save_feedback()

        print(f"\nFeedback saved! Overall score: {feedback['overall_score']:.2f}")
        return feedback

    def _automated_feedback(self, experience: TaskExperience) -> Dict[str, Any]:
        """Generate automated feedback based on success metrics."""
        feedback = {
            'quality': 4 if experience.final_success else 2,
            'correct': experience.final_success,
            'efficiency': 4 if experience.performance_metrics.get('duration', 10) < 5 else 3,
            'overall_score': 0.8 if experience.final_success else 0.3,
            'timestamp': time.time(),
            'task_id': experience.task_id,
            'automated': True
        }

        self.feedback_data.append(feedback)
        self._save_feedback()

        return feedback

    def _save_feedback(self) -> None:
        """Save feedback data to file."""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")

    def create_preference_pairs(self, min_score_diff: float = 0.3) -> List[PreferencePair]:
        """Create preference pairs for DPO training from feedback data."""
        pairs: List[PreferencePair] = []

        # Group feedback by task type
        task_groups: Dict[str, List[Dict[str, Any]]] = {}
        for feedback in self.feedback_data:
            # Would need to link back to experiences to get task info
            # Simplified for now
            task_key = "general"  # In practice, would group by actual task type
            if task_key not in task_groups:
                task_groups[task_key] = []
            task_groups[task_key].append(feedback)

        # Create pairs within each task group
        for task_type, feedbacks in task_groups.items():
            feedbacks.sort(key=lambda x: x['overall_score'], reverse=True)

            for i in range(len(feedbacks)):
                for j in range(i + 1, len(feedbacks)):
                    score_diff = feedbacks[i]['overall_score'] - feedbacks[j]['overall_score']

                    if score_diff >= min_score_diff:
                        # Create preference pair
                        pair = PreferencePair(
                            task_id=f"pair_{len(pairs)}",
                            task_description=f"Task type: {task_type}",
                            chosen_solution="# Higher rated solution",
                            rejected_solution="# Lower rated solution",
                            chosen_reasoning="Solution with higher human rating",
                            rejected_reasoning="Solution with lower human rating",
                            preference_score=score_diff,
                            timestamp=time.time()
                        )
                        pairs.append(pair)

        logger.info(f"Created {len(pairs)} preference pairs for DPO training")
        return pairs


class MemoryManager:
    """Main class coordinating all memory and feedback components."""

    def __init__(self, memory_file: str = "memory.txt"):
        self.structured_logger = StructuredLogger(memory_file)
        self.vector_store = VectorMemoryStore()
        self.feedback_interface = HumanFeedbackInterface()

    def process_new_experiences(self) -> List[TaskExperience]:
        """Process new experiences from memory file."""
        # Parse new experiences
        experiences = self.structured_logger.parse_memory_file()

        # Add to vector store for similarity search
        for experience in experiences:
            self.vector_store.add_experience(experience)

        return experiences

    def get_similar_experiences(self, task_description: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Get similar past experiences for learning."""
        return self.vector_store.find_similar_experiences(task_description, n_results)

    def collect_feedback_batch(self, experiences: List[TaskExperience], interactive: bool = False) -> List[Dict[str, Any]]:
        """Collect feedback on a batch of experiences."""
        feedback_results = []

        for experience in experiences:
            if not any(fb.get('task_id') == experience.task_id for fb in self.feedback_interface.feedback_data):
                feedback = self.feedback_interface.collect_feedback(experience, interactive)
                feedback_results.append(feedback)

        return feedback_results

    def generate_training_data(self) -> Tuple[List[TaskExperience], List[PreferencePair]]:
        """Generate structured training data for model fine-tuning."""
        experiences = self.structured_logger.experiences
        preference_pairs = self.feedback_interface.create_preference_pairs()

        return experiences, preference_pairs

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of all memory components."""
        return {
            "total_experiences": len(self.structured_logger.experiences),
            "successful_experiences": sum(1 for exp in self.structured_logger.experiences if exp.final_success),
            "total_feedback": len(self.feedback_interface.feedback_data),
            "vector_store_available": self.vector_store.collection is not None,
            "recent_experiences": self.structured_logger.experiences[-5:] if self.structured_logger.experiences else []
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize memory manager
    memory_manager = MemoryManager()

    # Process any new experiences
    print("Processing new experiences...")
    experiences = memory_manager.process_new_experiences()
    print(f"Found {len(experiences)} total experiences")

    # Get memory summary
    summary = memory_manager.get_memory_summary()
    print("\nMemory Summary:")
    print(f"- Total experiences: {summary['total_experiences']}")
    print(f"- Successful: {summary['successful_experiences']}")
    print(f"- Vector store: {'Available' if summary['vector_store_available'] else 'Not available'}")

    # Test similarity search
    if summary['total_experiences'] > 0:
        print("\nTesting similarity search...")
        similar = memory_manager.get_similar_experiences("Create a Python script for stock data")
        print(f"Found {len(similar)} similar experiences")

        for exp in similar[:2]:
            print(f"- {exp['metadata'].get('task_name', 'Unknown')} (similarity: {exp['similarity']:.2f})")

    # Collect feedback (automated for demo)
    if experiences:
        print("\nCollecting automated feedback...")
        feedback_results = memory_manager.collect_feedback_batch(experiences[:3], interactive=False)
        print(f"Collected feedback for {len(feedback_results)} experiences")

    # Generate training data
    experiences, pairs = memory_manager.generate_training_data()
    print("\nTraining data generated:")
    print(f"- Experiences: {len(experiences)}")
    print(f"- Preference pairs: {len(pairs)}")
