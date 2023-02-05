from .config import recall_paper_text
try:
    from cogdl.oag import oagbert
except:
    from cogdl import oagbert
import torch
import torch.nn.functional as F
from .config import oagbert_model_path

class OAG_BERT_Emb():
    def __init__(self, model_path=oagbert_model_path):
        self.tokenizer, self.model = oagbert(model_path)
        self.model.eval()
            
    def get_emb(self, input_dict):
        title = input_dict['title']
        if 'abstract' in input_dict:
            abstract = input_dict['abstract']
        else:
            abstract = ''
        if 'keywords' in input_dict:
            concepts = input_dict['keywords']
        else:
            concepts = []
        if 'venue' in input_dict:
            venue = input_dict['venue']
        else:
            venue = ''
        # authors and affiliations are lists.
        if 'authors' in input_dict:
            authors = input_dict['authors']
        else:
            authors = []
        if 'affiliations' in input_dict:
            affiliations = input_dict['affiliations']
        else:
            affiliations = []
        # build model inputs
        # print("Paper Info:\n{}\n{}\n{}\n{}\n{}\n{}".format(title,abstract,venue,authors,concepts,affiliations))
        input_ids, input_masks, token_type_ids, masked_lm_labels, position_ids, position_ids_second, masked_positions, num_spans = self.model.build_inputs(
            title=title, abstract=abstract, venue=venue, authors=authors, concepts=concepts, affiliations=affiliations
        )
        # run forward
        sequence_output, pooled_output = self.model.bert.forward(
            input_ids=torch.LongTensor(input_ids).unsqueeze(0),
            token_type_ids=torch.LongTensor(token_type_ids).unsqueeze(0),
            attention_mask=torch.LongTensor(input_masks).unsqueeze(0),
            output_all_encoded_layers=False,
            checkpoint_activations=False,
            position_ids=torch.LongTensor(position_ids).unsqueeze(0),
            position_ids_second=torch.LongTensor(position_ids).unsqueeze(0)
        )
        del abstract
        del concepts
        del venue
        del authors
        del affiliations
        del input_ids
        del input_masks
        del token_type_ids
        del masked_lm_labels
        del position_ids
        del position_ids_second
        del masked_positions
        del num_spans
        del sequence_output
        pooled_output = F.normalize(pooled_output, p=2, dim=1)
        emb = pooled_output.detach().numpy().astype('float32').flatten()
        # print("size before:{}, size after:{}".format(pooled_output.shape, emb.shape))
        del pooled_output
        return emb
