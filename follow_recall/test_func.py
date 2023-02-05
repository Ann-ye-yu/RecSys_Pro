import unittest
import focus_scholar_recall


class TestFunc(unittest.TestCase):

    hindex_dic = focus_scholar_recall.hinPapers_to_dic()
    nindex_dic = focus_scholar_recall.latestPapers_to_dic()
    user_id = "62106c1b757ab5a1ba7ccd7e"
    person_id = '53f48bdadabfaea7cd1cd2ff'
    paper_ids = ['53e9a082b7602d970296d7c1','5b67b46417c44aac1c8613a1']
    paper_id = '53e9a082b7602d970296d7c1'
    person_ids = ['53f46a3edabfaee43ed05f08', '53f48bdadabfaea7cd1cd2ff']
    person_id2 = '53f46a3edabfaee43ed05f08'
    def test00_distance(self):
        distance = focus_scholar_recall.distance('2021-04-10', 10)
        print(distance)
        self.assertTrue(isinstance(distance, float))
        self.assertTrue(distance > 0)
        self.assertTrue(distance < 1)

    def test01_hinPapers_to_dic(self):
        hindex_dic = focus_scholar_recall.hinPapers_to_dic()
        print(hindex_dic)
        self.assertTrue(isinstance(hindex_dic, dict))

    def test02_latestPapers_to_dic(self):
        nindex_dic = focus_scholar_recall.latestPapers_to_dic()
        print(nindex_dic)
        self.assertTrue(isinstance(nindex_dic, dict))

    def test03_get_time_and_citations(self):

        paper_list = focus_scholar_recall.get_time_and_citations(self.paper_ids)
        print(paper_list)
        self.assertTrue(isinstance(paper_list, list))

    def test04_get_papers_by_uids_from_latest_or_hindex(self):

        papers_List = focus_scholar_recall.get_papers_by_uids_from_latest_or_hindex(self.person_id, self.hindex_dic, 'followed_scholars')
        print(papers_List)
        self.assertTrue(isinstance(papers_List, list))

    def test05_get_coauthors_by_follow_person(self):

        coauthors_uids = focus_scholar_recall.get_coauthors_by_follow_person(self.person_id)
        print(coauthors_uids)
        self.assertTrue(isinstance(coauthors_uids, list))

    def test06_get_concern_author_papers(self):

        concern_high_papers, concern_new_papers = focus_scholar_recall.get_concern_author_papers(self.person_id2, self.hindex_dic, self.nindex_dic)
        print(concern_high_papers)
        print(concern_new_papers)
        self.assertTrue(isinstance(concern_high_papers, list))
        self.assertTrue(isinstance(concern_new_papers, list))

    def test07_get_coauthor_papers(self):

        coauthors_hindex_papers, coauthors_new_papers = focus_scholar_recall.get_coauthor_papers(self.person_id2, self.hindex_dic, self.nindex_dic)
        print(coauthors_hindex_papers)
        print(coauthors_new_papers)
        self.assertTrue(isinstance(coauthors_hindex_papers, list))
        self.assertTrue(isinstance(coauthors_new_papers, list))
        # self.assertTrue(len(concern_co_list) <= config.coauthor_number)

    def test08_get_similar_author_papers(self):

        sim_hindex_papers, sim_new_papers = focus_scholar_recall.get_similar_author_papers(self.person_id2, self.hindex_dic, self.nindex_dic)
        print(sim_hindex_papers)
        print(sim_new_papers)
        self.assertTrue(isinstance(sim_hindex_papers, list))
        self.assertTrue(isinstance(sim_new_papers, list))
        # self.assertTrue(len(concern_sim_list) <= config.sim_author_number)

    def test09_get_follow_author_id(self):

        following_ids = focus_scholar_recall.get_follow_author_id(self.user_id)
        print(following_ids)
        self.assertTrue(isinstance(following_ids, list))

    def test10_get_papers_by_follow_person(self):
        """测试函数get_papers_by_follow_person
                检查函数返回来的list是否正确
        """
        concern_paper_list = focus_scholar_recall.get_papers_by_follow_person(self.user_id, self.hindex_dic, self.nindex_dic)
        print("Number of recalls：{}".format(len(concern_paper_list)))
        print(concern_paper_list)
        self.assertTrue(isinstance(concern_paper_list, list))

    def test11_get_active_users(self):
        users_list_duplication = focus_scholar_recall.get_active_users()
        print(users_list_duplication)
        self.assertTrue(isinstance(users_list_duplication, list))

    def test12_papers_list_to_dic_list(self):
        concern_papers = [["53e9a645b7602d9702f745c5",0.8187307530779819,"similar_scholar"]]
        concern_papers_dic_list = focus_scholar_recall.papers_list_to_dic_list(concern_papers)
        print(concern_papers_dic_list)
        self.assertTrue(isinstance(concern_papers_dic_list, list))







if __name__ == '__main__':
    unittest.main()
