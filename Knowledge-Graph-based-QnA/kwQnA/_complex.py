# import re
import spacy


class ComplexFunc:

    def __init__(self):
        self.ent_pairs = list()
        self.nlp = spacy.load('en_core_web_sm')
        
    def get_time_place_from_sent(self,sentence):
        xdate =[]
        xplace =[]
        for i in sentence.ents:
            if i.label_ in ('DATE'):
                xdate.append(str(i))

            if i.label_ in ('GPE'):
                xplace.append(str(i))

        return xdate, xplace

    def find_obj(self, sentence, place, time):
        object_list = []

        for word in sentence:
            if word.dep_ in ('obj', 'dobj', 'pobj'):
                buffer_obj = word

                if str(word) in place and word.nbor(-1).dep_ in ('prep') and str(word.nbor(-1)) == "of":
                    pass
                else:
                    if str(word) not in time and str(word) not in place:
                        for child in word.subtree:
                            if child.dep_ in ('conj', 'dobj', 'pobj', 'obj') and (str(child) not in time) and (str(child) not in place):
                                if [i for i in child.lefts]:
                                    if child.nbor(-1).dep_ in ('nummod') and child.dep_ in ('dobj', 'obj','pobj'):
                                        child = str(child.nbor(-1)) + " " + str(child)
                                        object_list.append(str(child))

                                    elif child.nbor(-1).dep_ in ('punct'):
                                        if child.nbor(-2).dep_ in ('compound'):
                                            child = str(child.nbor(-2)) + str(child.nbor(-1)) + str(child)
                                            object_list.append(str(child))
                                        elif child.nbor(-2).dep_ in ('amod'):
                                            child = str(child.nbor(-2)) + str(child.nbor(-1)) + str(child)
                                            object_list.append(str(child))

                                    elif child.nbor(-1).dep_ in ('compound'):

                                        child_with_comp = ""
                                        for i in child.subtree:
                                            if i.dep_ in ('compound', 'nummod','quantmod'):
                                                if child_with_comp == "":
                                                    child_with_comp = str(i)
                                                else:
                                                    child_with_comp = child_with_comp +" "+ str(i)
                                            elif i.dep_ in ('cc'):
                                                break
                                        child = child_with_comp + " " + str(child)
                                        object_list.append(str(child))

                                    elif child.nbor(-1).dep_ in ('det'):
                                        object_list.append(str(child))

                                elif [i for i in child.rights]:
                                    if str(child.text) not in object_list:
                                        object_list.append(str(child.text))

                                    for a in child.children:
                                        if a.dep_ in ('conj'):
                                            if a.nbor(-1).dep_ in ('punct'):
                                                pass
                                            else:
                                                object_list.extend( [ str(a.text) ] )

                                else:
                                    if str(child) not in object_list:
                                        object_list.append(str(child))

                    elif str(word) in place and str(word.nbor(-1)) != "of":
                        if object_list == []:
                            object_list.append(str(word))
                        else:
                            pass
                    else:
                        if str(word) in time and object_list == []:
                            object_list.append(str(word))

        return object_list, buffer_obj

    def find_subj(self, sentence):
        subject_list = []
        dep_word = [word.dep_ for word in sentence]
        word_dep_count_subj = [dep_word.index(word) for word in dep_word if word in ('nsubj', 'subj', 'nsubjpass')]
        if word_dep_count_subj:
            word_dep_count_subj = word_dep_count_subj[0] + 1
        else:
            word_dep_count_subj = 1

        subject_final = ""
        for word in sentence:
            if word_dep_count_subj > 0:
                if word.dep_ in ('compound') or word.dep_ in ('nmod') or word.dep_ in ('amod') or word.dep_ in ('poss') or word.dep_ in ('case') or word.dep_ in ('nummod'):
                    if subject_final == "":
                        subject_final = str(word)
                        word_dep_count_subj = word_dep_count_subj - 1
                    elif word.dep_ in ('case'):
                        subject_final = subject_final+ "" +str(word)
                        word_dep_count_subj = word_dep_count_subj - 1
                    else:
                        subject_final = subject_final+ " " +str(word)
                        word_dep_count_subj = word_dep_count_subj - 1
                elif word.dep_ in ('nsubj', 'subj', 'nsubjpass'):
                    if subject_final == "":
                        subject_final = str(word)
                        subject_list.extend([str(a.text) for a in word.subtree if a.dep_ in ('conj')])
                        word_dep_count_subj = word_dep_count_subj - 1
                        break
                    else:
                        subject_final = subject_final+" "+str(word)
                        subject_list.extend([str(a.text) for a in word.subtree if a.dep_ in ('conj')])
                        word_dep_count_subj = word_dep_count_subj - 1
                        break
                else:
                    pass

        subject_list.append(subject_final)
        return subject_list

    def find_relation(self, buffer_obj):
        aux_relation = ""
        relation = [w for w in buffer_obj.ancestors if w.dep_ =='ROOT']

        if relation:
            relation = relation[0]
            sp_relation = relation
            if relation.nbor(1).pos_ in ('VERB'):
                if relation.nbor(2).dep_ in ('xcomp'):
                    relation = ' '.join((str(relation), str(relation.nbor(1)), str(relation.nbor(2))))
                else:
                    relation = str(relation)
                    if str(sp_relation.nbor(2)) != 'and':
                        if sp_relation.nbor(1).dep_ in ('xcomp'):
                            aux_relation = str(sp_relation.nbor(1))
                        else:
                            aux_relation = str(sp_relation.nbor(2))
            elif relation.nbor(1).pos_ in ('ADP', 'PART') and relation.nbor(1).dep_ in ('aux') and str(relation.nbor(1)) == 'to':
                relation = " ".join((str(relation), str(relation.nbor(1))))
                if str(sp_relation.nbor(2)) != 'and':
                    aux_relation = str(sp_relation.nbor(2))
            elif relation.nbor(1).dep_ in ('prep') and str(relation.nbor(1)) == 'to' and (relation.nbor(1)).dep_ not in ('obj','dobj','pobj','det'):
                relation = " ".join((str(relation), str(relation.nbor(1))))
            else:
                relation = str(relation)
        else:
            relation = 'unknown'

        return relation, aux_relation


    def find_why(self, sentence):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(sentence)

        root = next(token for token in doc if token.dep_ == "ROOT")
        subject = next(token for token in root.lefts if token.dep_ in ["nsubj", "nsubjpass"])

        subordinating_conjunctions = ["because", "since", "due to"]
        if any(token.text in subordinating_conjunctions for token in root.lefts):
            subject_and_descendants = [token.text for token in subject.subtree]
            while (
                subject_and_descendants[-1].pos_ in ["ADJ", "ADV"]
                or subject_and_descendants[-1].dep_ in ["acomp", "amod", "advmod"]
            ):
                subject_and_descendants.extend([token.text for token in subject_and_descendants[-1].subtree])
        else:
            subject_and_descendants = [subject.text]

        reasons = subject_and_descendants + [
            token.text for sent in doc.sents for token in sent if token.dep_ in ["advcl", "amod", "advmod", "acomp"]
        ]

        answer = " ".join(reasons)

        return answer
  
    
    def normal_sent(self, sentence):
        time, place = self.get_time_place_from_sent(sentence)

        subject_list, object_list, cause_list = [], [], []

        aux_relation, child_with_comp = "", ""

        subject_list = self.find_subj(sentence)
        object_list, buffer_obj = self.find_obj(sentence, place, time)
        relation, aux_relation = self.find_relation(buffer_obj)
        

        self.ent_pairs = []

        if time:
            time = time[0]
        else:
            time = ""

        if place:
            place = place[0]
        else:
            place = ""

        if 'because' in sentence.text.lower() or 'since' in sentence.text.lower() or 'due to' in sentence.text.lower():
            cause_list.append(self.find_why(sentence))
        else:
            cause_list.append("")

        pa, pb, pc =[], [], []
        for m in subject_list:
            pa.append([m])

        for n in object_list:
            pb.append([n])

        for y in cause_list:
            pc.append([y])
            

        for m in range(0, len(pa)):
            for n in range(0, len(pb)):
                self.ent_pairs.append([str(pa[m][0]).lower(), str(relation).lower(),str(aux_relation).lower(), str(pb[n][0]).lower(), str(time), str(place), str(pc).lower()])
        return self.ent_pairs

    def question_pairs(self, question__):

        questionNLPed = self.nlp(question__)
        maybe_object = ([i for i in questionNLPed if i.dep_ in ('obj', 'pobj', 'dobj')])
        maybe_place, maybe_time = [], []
        aux_relation = ""
        maybe_time, maybe_place = self.get_time_place_from_sent(questionNLPed)
        object_list = []

        for obj in questionNLPed:
            objectNEW = obj

            # FOR WHO
            if obj.dep_ in ('obj', 'dobj', 'pobj', 'xcomp') and str(obj).lower() != "what":
                buffer_obj = obj

                if obj.dep_ in ('xcomp') and obj.nbor(-1).dep_ in ('aux') and obj.nbor(-2).dep_ in ('ROOT'):
                    continue

                if str(obj) in maybe_place and obj.nbor(-1).dep_ in ('prep') and str(obj.nbor(-1)) == "of":
                    pass
                else:
                    if str(obj) not in maybe_time and str(obj) not in maybe_place:
                        for child in obj.subtree:
                            if child.dep_ in ('conj', 'dobj', 'pobj', 'obj'):
                                if [i for i in child.lefts]:
                                    if child.nbor(-1).dep_ in ('punct') and child.nbor(-2).dep_ in ('compound'):
                                        child = str(child.nbor(-2)) + str(child.nbor(-1)) + str(child)
                                        object_list.append(str(child))

                                    elif child.nbor(-1).dep_ in ('compound'):
                                        child_with_comp = ""
                                        for i in child.subtree:
                                            if i.dep_ in ('compound', 'nummod','quantmod'):
                                                if child_with_comp == "":
                                                    child_with_comp = str(i)
                                                else:
                                                    child_with_comp = child_with_comp +" "+ str(i)
                                            elif i.dep_ in ('cc'):
                                                break
                                        child = child_with_comp + " " + str(child)
                                        object_list.append(str(child))

                                    elif child.nbor(-1).dep_ in ('det'):
                                        object_list.append(str(child))

                                elif [i for i in child.rights]:
                                    if str(child.text) not in object_list:
                                        object_list.append(str(child.text))

                                    for a in child.children:
                                        if a.dep_ in ('conj'):
                                            if a.nbor(-1).dep_ in ('punct'):
                                                pass
                                            else:
                                                object_list.extend( [ str(a.text) ] )

                                else:
                                    if str(child) not in object_list:
                                        object_list.append(str(child))

                            elif obj.dep_ in ('xcomp'):
                                object_list.append(str(obj))

                    elif str(obj) in maybe_place and str(obj.nbor(-1)) != "of":
                        object_list.append(str(obj))
                    else:
                        if str(obj) in maybe_time and object_list == []:
                            object_list.append(str(obj))

                obj = object_list[-1]

                relation = [w for w in objectNEW.ancestors if w.dep_ =='ROOT']
                if relation:
                    relation = relation[0]
                    sp_relation = relation
                    if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                        if relation.nbor(2).dep_ in ('xcomp'):
                            aux_relation = str(relation.nbor(2))
                            relation = str(relation)+" "+str(relation.nbor(1))
                        else:
                            relation = str(relation)

                    subject = [a for a in sp_relation.lefts if a.dep_ in ('subj', 'nsubj','nsubjpass')]  # identify subject nodes
                    if subject:
                        subject = subject[0]
                    else:
                        subject = 'unknown'
                else:
                    relation = 'unknown'

                self.ent_pairs = []

                if maybe_time and maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str(maybe_place[0]).lower()])
                elif maybe_time:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str("").lower()])
                elif maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str(maybe_place[0]).lower()])
                else:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str("").lower()])
                return self.ent_pairs
            
            # FOR WHAT QUESTIONS
            elif str(obj).lower() == "what":
                relation = [w for w in objectNEW.ancestors if w.dep_ =='ROOT']
                if relation:
                    relation = relation[0]
                    sp_relation = relation
                    if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                        if relation.nbor(2).dep_ in ('xcomp'):
                            aux_relation = str(relation.nbor(2))
                            relation = str(relation)+" "+str(relation.nbor(1))
                        else:
                            relation = str(relation)

                    subject = self.find_subj(questionNLPed)
                    subject = subject[-1]

                else:
                    relation = 'unknown'

                self.ent_pairs = []
                if maybe_time and maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str(maybe_place[0]).lower()])
                elif maybe_time:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str("").lower()])
                elif maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str(maybe_place[0]).lower()])
                else:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str("").lower()])
                return self.ent_pairs

            # FOR WHERE QUESTIONS 
            elif obj.dep_ in ('advmod'):
                if str(obj).lower() == 'where':
                    relation = [w for w in obj.ancestors if w.dep_ =='ROOT']
                    if relation:
                        relation = relation[0]
                        sp_relation = relation
                        if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                            if relation.nbor(2).dep_ in ('xcomp'):
                                aux_relation = str(relation.nbor(2))
                                relation = str(relation)+" "+str(relation.nbor(1))
                            else:
                                relation = str(relation)

                        subject = self.find_subj(questionNLPed)
                        subject = subject[-1]

                    else:
                        relation = 'unknown'

                    self.ent_pairs = []
                    if maybe_object:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("").lower(), str("where").lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("").lower(), str("where").lower()])
                    else:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("").lower(), str("where").lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("").lower(), str("where").lower()])

                    return self.ent_pairs

                # FOR WHEN QUESTIONS
                elif str(obj).lower() == 'when':
                    relation = [w for w in obj.ancestors if w.dep_ =='ROOT']
                    if relation:
                        relation = relation[0]
                        sp_relation = relation
                        if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                            if relation.nbor(2).dep_ in ('xcomp'):
                                relation = ' '.join((str(relation), str(relation.nbor(1)), str(relation.nbor(2))))
                            else:
                                relation = ' '.join((str(relation), str(relation.nbor(1))))

                        for left_word in sp_relation.lefts:
                            if left_word.dep_ in ('subj', 'nsubj','nsubjpass'):
                                if [i for i in left_word.lefts]:
                                    for left_of_left_word in left_word.lefts:
                                        subject = str(left_of_left_word) + " " + str(left_word)
                                else:
                                    subject = str(left_word)

                    else:
                        relation = 'unknown'

                    self.ent_pairs = []
                    if maybe_object:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str("").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str("").lower()])
                    else:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str("").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str("").lower()])

                    
                
                # Handle "why" questions
                elif str(obj).lower() == 'why':
                    # Extract relevant information for "why" questions
                    subject = self.find_subj(questionNLPed)
                    subject = subject[-1] if subject else ""
                    
                    # Extract the reason or cause from the context
                    reason = self.find_why(questionNLPed)

                    self.ent_pairs = []
                    if maybe_object:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), "cause", str(aux_relation).lower(), str(maybe_object[-1]).lower(), str(reason).lower(), str(maybe_place[0]).lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), "cause", str(aux_relation).lower(), str(maybe_object[-1]).lower(), str(reason).lower(), str("").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), "cause", str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("").lower(), str(maybe_place[0]).lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), "cause", str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("").lower(), str("").lower()])
                    else:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), "cause", str(aux_relation).lower(), str("").lower(), str(reason).lower(), str(maybe_place[0]).lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), "cause", str(aux_relation).lower(), str("").lower(), str(reason).lower(), str("").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), "cause", str(aux_relation).lower(), str("").lower(), str("").lower(), str(maybe_place[0]).lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), "cause", str(aux_relation).lower(), str("").lower(), str("").lower(), str("").lower()])

                    return self.ent_pairs
