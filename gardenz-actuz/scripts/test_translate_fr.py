import copy
import unittest
from translate_fr import prepare_documents, source_hash, valid_translation, clean_french, english_input

class TranslationTests(unittest.TestCase):
    def item(self, language='en'):
        return dict(id='one', language=language, title='Medical cannabis research', excerpt='The study follows 100 patients.', url='https://example.org/one')

    def translator(self, language, texts):
        return ['Recherche sur le cannabis médical' if text == 'Medical cannabis research' else 'L’étude suit 100 patients.' for text in texts]

    def test_political_sense_does_not_change_literal_floating(self):
        self.assertIn('Committee suggests', english_input('Senate Committee Floats Marijuana As Alternative'))
        self.assertEqual(english_input('A leaf floats on the water'), 'A leaf floats on the water')
        self.assertIn('draft law', english_input('cannabis banking bill'))

    def test_observed_spelling_and_count_formatting(self):
        self.assertEqual(clean_french('Substances psihédéliques et article de opinion'), 'Substances psychédéliques et article d’opinion')
        self.assertEqual(clean_french('3.744 patients', 'de'), '3 744 patients')
        self.assertEqual(clean_french('0.003 mg', 'de'), '0.003 mg')
        self.assertEqual(clean_french('médicaments à base de cannabinoïdes', 'en', 'Cannabinoid medicine'), 'médecine des cannabinoïdes')

    def test_preserves_currency_and_pending_legal_status(self):
        self.assertEqual(clean_french('12 millions d’euros', 'en', '£12m recapitalisation'), '12 millions de livres sterling')
        self.assertEqual(clean_french('12 millions d’euros', 'en', '£12m and €12m'), '12 millions d’euros')
        self.assertEqual(clean_french('Plusieurs lois sur la légalisation', 'en', 'Several legalization bills'), 'Plusieurs projets de loi visant la légalisation')
        self.assertEqual(english_input('£12m'), '12 million British pounds')

    def test_preserves_originals_and_reuses_daily_duplicate(self):
        item=self.item(); french=dict(id='fr',language='fr',title='Titre français',excerpt='Extrait',url='https://example.org/fr')
        docs=[{'items':[item,french]},{'items':[copy.deepcopy(item)]}]
        calls=[]
        def translate(language,texts): calls.append((language,texts));return self.translator(language,texts)
        self.assertEqual(prepare_documents(docs,translate,now='test'),[])
        self.assertEqual(len(calls),1)
        self.assertEqual(item['title'],'Medical cannabis research')
        self.assertEqual(item['url'],'https://example.org/one')
        self.assertEqual(item['translation']['title'],'Recherche sur le cannabis médical')
        self.assertNotIn('translation',french)
        self.assertEqual(docs[0]['translationStatus']['available'],1)
        self.assertEqual(docs[1]['items'][0]['translation'],item['translation'])

    def test_exact_cache_hit_needs_no_model(self):
        docs=[{'items':[self.item()]}]
        prepare_documents(docs,self.translator)
        def forbidden(*args):raise AssertionError('Model should not be loaded')
        self.assertEqual(prepare_documents(docs,forbidden),[])
        self.assertTrue(valid_translation(docs[0]['items'][0],docs[0]['items'][0]['translation']))

    def test_changed_excerpt_invalidates_translation(self):
        item=self.item();docs=[{'items':[item]}];prepare_documents(docs,self.translator)
        old=source_hash(item);item['excerpt']='The study follows 200 patients.'
        self.assertNotEqual(source_hash(item),old)
        self.assertFalse(valid_translation(item,item['translation']))
        def offline(*args):raise RuntimeError('Model unavailable')
        self.assertEqual(prepare_documents(docs,offline),['en'])
        self.assertNotIn('translation',item)
        self.assertEqual(item['excerpt'],'The study follows 200 patients.')
        self.assertEqual(docs[0]['translationStatus']['status'],'partial')

    def test_model_failure_keeps_existing_valid_translations(self):
        item=self.item();docs=[{'items':[item]}];prepare_documents(docs,self.translator)
        previous=copy.deepcopy(item['translation']); german=self.item('de');german['id']='two';docs[0]['items'].append(german)
        def offline(*args):raise RuntimeError('Unavailable')
        self.assertEqual(prepare_documents(docs,offline),['de'])
        self.assertEqual(item['translation'],previous)
        self.assertEqual(docs[0]['translationStatus']['available'],1)
        self.assertEqual(docs[0]['translationStatus']['eligible'],2)

    def test_finished_batches_survive_later_interruption(self):
        items=[dict(self.item(),id=str(n),title='Medical cannabis research '+str(n)) for n in range(3)]
        docs=[{'items':items}];snapshots=[];calls=[]
        def translate(lang,texts):
            calls.append(texts)
            if len(calls)==2:raise RuntimeError('Step deadline')
            return ['Texte français' for text in texts]
        failures=prepare_documents(docs,translate,checkpoint=lambda:snapshots.append(copy.deepcopy(docs)))
        self.assertEqual(failures,['en'])
        self.assertTrue(any(s[0]['translationStatus']['available']==2 for s in snapshots))
        self.assertEqual(docs[0]['translationStatus']['available'],2)
        self.assertIn('translation',items[0]);self.assertNotIn('translation',items[2])

    def test_missing_output_is_not_published_as_success(self):
        docs=[{'items':[self.item()]}]
        self.assertEqual(prepare_documents(docs,lambda lang,texts:[]),['en'])
        self.assertNotIn('translation',docs[0]['items'][0])
        self.assertEqual(docs[0]['translationStatus']['available'],0)

if __name__=='__main__':unittest.main()
