import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import language_fingerprints

if __name__ == "__main__":
    # 示例：加载已有指纹文件
    detector = language_fingerprints.LanguageDetector("data/language_fingerprints.json")

    # 测试
    text1 = "中华人民共和国是世界上人口最多的国家。"
    text2 = "This is an English sentence."
    text3 = "これは日本語の文です。"
    text4 = "안녕하세요 저는 한국 사람입니다."
    text5 = "你好，我是一个中国人123542ABCDEWRSSSABCDEWRSSSABCDEWRSSSABCDEWRSSSABCDEWRSSSABCDEWRSSS3123123123。"

    for txt in [text1, text2, text3, text4, text5]:
        lang, score, all_scores = detector.detect(txt)
        print(f"输入: {txt}")
        print(f"预测语种: {lang}, 置信度: {score:.4f}")
        print(f"所有分数: {all_scores}\n")
