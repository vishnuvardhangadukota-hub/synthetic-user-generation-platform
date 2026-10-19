import React, { useEffect, useState } from 'react';
import {
  ClipboardList,
  Plus,
  Play,
  CheckCircle2,
  ListFilter,
  MessageSquare,
  HelpCircle,
  Sparkles,
  BarChart,
  User,
} from 'lucide-react';
import { surveysApi } from '@/services/api';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Input, Textarea, Select } from '@/components/ui/FormControls';
import { EmptyState } from '@/components/ui/EmptyState';
import { useToast } from '@/context/ToastContext';
import type {
  Survey,
  SurveyQuestion,
  SurveyResponsesGrouped,
  QuestionGroupedResponses,
} from '@/types';

interface ExperimentSurveysTabProps {
  experimentId: string;
  hasPersonas: boolean;
  onRefreshParent: () => void;
}

export const ExperimentSurveysTab: React.FC<ExperimentSurveysTabProps> = ({
  experimentId,
  hasPersonas,
  onRefreshParent,
}) => {
  const { success, error } = useToast();

  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [selectedSurvey, setSelectedSurvey] = useState<Survey | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Grouped responses for selected survey
  const [groupedResponses, setGroupedResponses] = useState<SurveyResponsesGrouped | null>(null);
  const [isLoadingResponses, setIsLoadingResponses] = useState(false);

  // Create Survey Modal
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  // Add Question Modal
  const [questionModalOpen, setQuestionModalOpen] = useState(false);
  const [qText, setQText] = useState('');
  const [qType, setQType] = useState<
    'rating' | 'yes_no' | 'short_answer' | 'opinion' | 'open_ended'
  >('yes_no');
  const [isAddingQuestion, setIsAddingQuestion] = useState(false);

  // Simulation Running State
  const [isRunning, setIsRunning] = useState(false);

  const fetchSurveys = async (selectSurveyId?: string) => {
    try {
      setIsLoading(true);
      const data = await surveysApi.listByExperiment(experimentId);
      setSurveys(data);
      if (data.length > 0) {
        const target = selectSurveyId
          ? data.find((s) => s.id === selectSurveyId) || data[0]
          : selectedSurvey
          ? data.find((s) => s.id === selectedSurvey.id) || data[0]
          : data[0];
        setSelectedSurvey(target);
        if (target) {
          fetchResponses(target.id);
        }
      } else {
        setSelectedSurvey(null);
        setGroupedResponses(null);
      }
    } catch (err: any) {
      error('Failed to load surveys', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchResponses = async (surveyId: string) => {
    try {
      setIsLoadingResponses(true);
      const res = await surveysApi.getResponsesGrouped(surveyId);
      setGroupedResponses(res);
    } catch {
      setGroupedResponses(null);
    } finally {
      setIsLoadingResponses(false);
    }
  };

  useEffect(() => {
    fetchSurveys();
  }, [experimentId]);

  const handleSelectSurvey = (survey: Survey) => {
    setSelectedSurvey(survey);
    fetchResponses(survey.id);
  };

  const handleCreateSurvey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      setIsCreating(true);
      const created = await surveysApi.create(experimentId, {
        title: newTitle.trim(),
        description: newDesc.trim() || undefined,
      });
      success('Survey created', `"${created.title}" was created.`);
      setCreateModalOpen(false);
      setNewTitle('');
      setNewDesc('');
      await fetchSurveys(created.id);
      onRefreshParent();
    } catch (err: any) {
      error('Failed to create survey', err.message);
    } finally {
      setIsCreating(false);
    }
  };

  const handleAddQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSurvey || !qText.trim()) return;
    try {
      setIsAddingQuestion(true);
      await surveysApi.addQuestion(selectedSurvey.id, {
        question_text: qText.trim(),
        question_type: qType,
        order: (selectedSurvey.questions?.length || 0) + 1,
      });
      success('Question added', 'Question added to survey.');
      setQuestionModalOpen(false);
      setQText('');
      setQType('yes_no');
      await fetchSurveys(selectedSurvey.id);
      onRefreshParent();
    } catch (err: any) {
      error('Failed to add question', err.message);
    } finally {
      setIsAddingQuestion(false);
    }
  };

  const handleRunSimulation = async () => {
    if (!selectedSurvey) return;
    if (!hasPersonas) {
      error(
        'No personas available',
        'Please generate synthetic personas first before executing a survey.'
      );
      return;
    }
    if (!selectedSurvey.questions || selectedSurvey.questions.length === 0) {
      error('No questions found', 'Add at least one question before running the survey simulation.');
      return;
    }

    try {
      setIsRunning(true);
      const res = await surveysApi.run(selectedSurvey.id);
      success(
        'Simulation Complete',
        `Generated ${res.total_responses_generated} responses across ${res.total_personas} synthetic personas.`
      );
      await fetchResponses(selectedSurvey.id);
      await fetchSurveys(selectedSurvey.id);
      onRefreshParent();
    } catch (err: any) {
      error('Simulation failed', err.message);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Survey Simulation Mode</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Design structured surveys and simulate responses across synthetic personas.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => setCreateModalOpen(true)}
        >
          Create Survey
        </Button>
      </div>

      {surveys.length === 0 ? (
        <EmptyState
          icon={<ClipboardList className="w-6 h-6 text-indigo-600" />}
          title="No surveys created yet"
          description="Create a survey and add rating, yes/no, or open-ended questions to test with your synthetic persona cohort."
          actionLabel="Create Survey"
          onAction={() => setCreateModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Survey Selector List (1 Col) */}
          <div className="lg:col-span-1 space-y-2">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-1">
              Surveys ({surveys.length})
            </h4>
            <div className="space-y-1.5">
              {surveys.map((s) => {
                const isSelected = selectedSurvey?.id === s.id;
                return (
                  <button
                    key={s.id}
                    onClick={() => handleSelectSurvey(s)}
                    className={`w-full text-left p-3.5 rounded-xl border transition-all ${
                      isSelected
                        ? 'bg-indigo-50/80 border-indigo-200 text-slate-900 shadow-xs'
                        : 'bg-white border-slate-200/80 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="font-semibold text-xs line-clamp-1">{s.title}</span>
                      <Badge
                        variant={s.status === 'completed' ? 'success' : 'default'}
                        size="sm"
                      >
                        {s.status}
                      </Badge>
                    </div>
                    <span className="text-[11px] text-slate-400">
                      {s.questions?.length || 0} questions
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Active Survey Workspace (3 Cols) */}
          <div className="lg:col-span-3 space-y-6">
            {selectedSurvey && (
              <>
                {/* Survey Actions & Questions list */}
                <Card>
                  <CardHeader>
                    <div>
                      <div className="flex items-center gap-2">
                        <CardTitle>{selectedSurvey.title}</CardTitle>
                        <Badge
                          variant={selectedSurvey.status === 'completed' ? 'success' : 'default'}
                          size="sm"
                        >
                          {selectedSurvey.status}
                        </Badge>
                      </div>
                      {selectedSurvey.description && (
                        <CardDescription>{selectedSurvey.description}</CardDescription>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        leftIcon={<Plus className="w-3.5 h-3.5" />}
                        onClick={() => setQuestionModalOpen(true)}
                      >
                        Add Question
                      </Button>

                      <Button
                        variant="primary"
                        size="sm"
                        leftIcon={<Play className="w-3.5 h-3.5" />}
                        onClick={handleRunSimulation}
                        isLoading={isRunning}
                        disabled={!hasPersonas || (selectedSurvey.questions?.length || 0) === 0}
                      >
                        Run Simulation
                      </Button>
                    </div>
                  </CardHeader>

                  <CardContent className="p-5">
                    {/* Questions summary */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                        Survey Questions ({selectedSurvey.questions?.length || 0})
                      </h4>

                      {(!selectedSurvey.questions || selectedSurvey.questions.length === 0) ? (
                        <div className="p-4 rounded-xl border border-dashed border-slate-200 text-center text-xs text-slate-400">
                          No questions added yet. Click "Add Question" above.
                        </div>
                      ) : (
                        <div className="space-y-2">
                          {selectedSurvey.questions.map((q, idx) => (
                            <div
                              key={q.id}
                              className="p-3 rounded-lg border border-slate-100 bg-slate-50/70 flex items-center justify-between gap-3 text-xs"
                            >
                              <div className="flex items-center gap-2.5">
                                <span className="font-bold text-slate-400 w-5">#{idx + 1}</span>
                                <span className="font-medium text-slate-900">{q.question_text}</span>
                              </div>
                              <Badge variant="purple" size="sm">
                                {q.question_type}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Grouped Responses Side-by-Side Breakdown */}
                {groupedResponses && groupedResponses.grouped_by_question?.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Cohort Responses Comparison</CardTitle>
                      <CardDescription>
                        Side-by-side responses grouped by question across all personas
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-5 space-y-6">
                      {groupedResponses.grouped_by_question.map((gq) => (
                        <div
                          key={gq.question_id}
                          className="rounded-xl border border-slate-200/80 overflow-hidden"
                        >
                          <div className="p-3.5 bg-slate-50 border-b border-slate-200/80 flex items-center justify-between">
                            <span className="font-semibold text-xs text-slate-900">
                              {gq.question_text}
                            </span>
                            <Badge variant="outline" size="sm">
                              {gq.question_type}
                            </Badge>
                          </div>

                          <div className="divide-y divide-slate-100 p-2">
                            {gq.responses.map((resp) => (
                              <div key={resp.id} className="p-3 hover:bg-slate-50/50 rounded-lg">
                                <div className="flex items-center justify-between mb-1.5">
                                  <span className="text-xs font-semibold text-indigo-700 flex items-center gap-1.5">
                                    <User className="w-3.5 h-3.5" />
                                    {resp.persona_name || resp.persona_id}
                                  </span>
                                  {resp.rating_score != null && (
                                    <Badge variant="warning" size="sm">
                                      Rating: {resp.rating_score} / 5
                                    </Badge>
                                  )}
                                </div>
                                <p className="text-xs text-slate-800 font-medium">{resp.answer}</p>
                                {resp.reasoning && (
                                  <p className="text-[11px] text-slate-500 mt-1 italic">
                                    Reasoning: {resp.reasoning}
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Create Survey Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Create New Survey"
        description="Add a survey to evaluate pricing, feature demand, or onboarding flow."
        maxWidth="md"
      >
        <form onSubmit={handleCreateSurvey} className="space-y-4">
          <Input
            label="Survey Title"
            placeholder="e.g., Feature Prioritization Survey"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
          />

          <Textarea
            label="Description (Optional)"
            placeholder="Context or research intent for this survey..."
            rows={2}
            value={newDesc}
            onChange={(e) => setNewDesc(e.target.value)}
          />

          <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2.5">
            <Button
              variant="outline"
              size="md"
              type="button"
              onClick={() => setCreateModalOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="primary" size="md" type="submit" isLoading={isCreating}>
              Create Survey
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Question Modal */}
      <Modal
        isOpen={questionModalOpen}
        onClose={() => setQuestionModalOpen(false)}
        title="Add Question to Survey"
        description="Configure question text and response format."
        maxWidth="md"
      >
        <form onSubmit={handleAddQuestion} className="space-y-4">
          <Input
            label="Question Text"
            placeholder="e.g., Would you pay ₹299/month for premium delivery?"
            value={qText}
            onChange={(e) => setQText(e.target.value)}
            required
          />

          <Select
            label="Question Type"
            value={qType}
            onChange={(e) => setQType(e.target.value as any)}
          >
            <option value="yes_no">Yes / No</option>
            <option value="rating">Rating (1 to 5 Stars / Scale)</option>
            <option value="short_answer">Short Answer</option>
            <option value="opinion">Opinion</option>
            <option value="open_ended">Open Ended</option>
          </Select>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2.5">
            <Button
              variant="outline"
              size="md"
              type="button"
              onClick={() => setQuestionModalOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="primary" size="md" type="submit" isLoading={isAddingQuestion}>
              Add Question
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
