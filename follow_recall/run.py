import focus_scholar_recall
import config
import click

@click.command()
# @click.option("--start_date", default=f"{current_year}-1-1", help="Grab the start date of the paper. input format: "
#                                                                   "%Y-%m-%d")
@click.option("--active-start-time", default=config.ACTIVE_START_TIME, help="Grab the start date of the paper. input format: "
                                                                  "%Y-%m-%d")
@click.option("--active-end-time", default=config.ACTIVE_END_TIME, help="Grab the end date of the paper. input format: %Y-%m-%d")
def main(active_start_time,active_end_time):
    focus_scholar_recall.delete_old_files()
    focus_scholar_recall.get_papers_by_follow_active_persons(active_start_time,active_end_time)

if __name__ == '__main__':
    '''
Returns:
        1. 基于关注学者的召回
        （1） 关注学者最新发表的论文和高引论文
            a. 关于最新发表的论文：从学者动态信息表里召回；
            b. 关于高引论文：按照物料池高引论文的标准来
            c. 召回数量可以暂定50条，后续再调整
        （2） 关注学者的合作学者、师生最新发表的论文和高引论文
            a. 师生关系优先，合作关系按照合作紧密度依次降低，取10位学者，不足的有多少取多少
            b. 新发表论文也是从学者的动态信息表里取，高引论文按照物料池高引标准来
            c. 召回数量可以暂定50条，后续再调整
        （3） 关注学者的相似学者最新发表的论文和高引论文
            a. 通过接口获取学者的相似学者，取前10位，不足的有多少取多少
            b. 取新论文和高引论文的规则同上
            c. 召回数量可以暂定50条，后续再调整
    '''
    # 150 recall data are returned
    
    main()

