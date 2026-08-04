

### Descripción del proyecto
Este proyecto tiene como objetivo realizar una detección rápida de codificaciones en una gran cantidad de archivos de texto para facilitar el trabajo de limpieza de datos del proyecto de corpus [MNBVC](https://github.com/esbatmop/MNBVC).

#### Instalación del módulo
```
pip install charset-mnbvc
```

#### URL de charset-mnbvc en PyPI:
https://pypi.org/project/charset-mnbvc/

##### Obtener la codificación de todos los archivos en un directorio
```
from charset_mnbvc import api

file_count, results = api.from_dir(
    folder_path=ifolder_path,
)

for result in results:
    print(f"文件名: {result[0]}, 编码: {result[1]}")

```

##### Obtener la codificación de un solo archivo
```
from charset_mnbvc import api

file_path = "test.txt"
coding_name = api.get_cn_charset(file_path)
print(f"文件名: {file_path}, 编码: {coding_name}")

```

##### Detectar la proporción de chino e inglés en un documento
```
from charset_mnbvc import api

with open("tests/fixtures/10.txt", "rb") as f:
    data = f.read()
    ret, percentage = api.check_zh_en(data)
    print(f"是否为中英文文档: {ret}, 比例: {percentage}")
```

##### Obtener la codificación de datos binarios
```
from charset_mnbvc import api

with open("tests/fixtures/10.txt", "rb") as f:
    data = f.read()
    coding_name = api.from_data(data=data, mode=2)
    print(f"数据编码: {coding_name}")
```

###### Convertir la codificación de datos binarios
```
from charset_mnbvc import api

source_data = b'\xb5\xda\xcb\xc4\xd5\xc2' #gbk 编码

ret = api.convert_encoding(
    source_data=source_data,
    source_encoding="gbk",
    target_encoding="utf-8",
)
print(ret)
```

###### Intentar reparar datos con caracteres corruptos
```
from charset_mnbvc import api
data_1 = "变巨"

result_1 = api.fix_data(s=data_1)
print(f"修复测试1: {result_1}")

from      | to        | origin | guess
-----------------------------------
utf-8     | gbk       | 变巨 | 鍙樺法
utf-8     | gb18030   | 变巨 | 鍙樺法
utf-8     | BIG5      | 变巨 | ���撌�
utf-8     | shift_jis | 变巨 | 蜿伜ｷｨ
utf-8     | euc_kr    | 变巨 | ���藥�
utf-8     | ascii     | 变巨 | ������
utf-8     | utf_16    | 变巨 | 迥ꢷ
utf-8     | cp1252    | 变巨 | å�˜å·¨
gbk       | utf-8     | 变巨 | ���
gbk       | gb18030   | 变巨 | 变巨
gbk       | BIG5      | 变巨 | 曹操
gbk       | shift_jis | 变巨 | ｱ萓ﾞ
gbk       | euc_kr    | 变巨 | 긴앵
gbk       | ascii     | 变巨 | ����
```

###### Herramienta de detección de proporción de caracteres corruptos
```
from charset_mnbvc import api
file_path = "/Users/alan/mywork/mnbvc/tests/fixtures/errors/48.txt"
ret, ratio = api.check_disorder_chars(file_path=file_path, threshold=0.05)
print(f"包含乱码的字符拷锟斤等字符, 乱码比例约:{round(float(ratio)*100)}%" if ret else "未找到乱码的字符，请注意调节阈值")

结果:
包含乱码的字符拷锟斤等字符, 乱码比例约:28%

```

###### Especificar el rango de codificaciones a detectar
En algunos casos, puede resultar útil que la detección de codificación solo devuelva los formatos esperados, por lo que puede emplearse este método (actualmente solo es válido para `mode=1`). La razón para diseñar este modo es que, en la mayoría de los casos, la codificación de textos cortos no puede identificarse correctamente y podría generar falsos positivos; por ejemplo, una codificación `gbk` podría identificarse erróneamente como `utf-8` u otro formato. Para más detalles, consulte https://wiki.mnbvc.org/doku.php/%E7%9F%AD%E6%96%87%E6%9C%AC%E6%97%A0%E6%B3%95%E6%AD%A3%E7%A1%AE%E6%A3%80%E6%B5%8B%E7%BC%96%E7%A0%81%E7%9A%84%E9%97%AE%E9%A2%98
```
from charset_mnbvc import api
data = b'\xd6\xa7\xb3\xc5\xb2\xc4\xc1\xcf/Code/p_3_1.m'
coding_name = api.get_cn_charset(
    source_data=data,
    source_type="data",
    mode=1,
    special_encodings=["gbk"]
)
print(coding_name)
```



###### Herramienta de detección de huellas de idioma
```
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

返回结果
输入: 中华人民共和国是世界上人口最多的国家。
预测语种: Chinese_Simplified, 置信度: 0.8800
所有分数: {'Latin': 0.0, 'Traditional_Chinese': 0.0, 'Japanese_Hiragana': 0.0, 'Simplified_Chinese': 0.008278027340893137, 'Korean_Hangul': 0.0, 'Cyrillic': 0.0, 'Thai': 0.0, 'Japanese_Katakana': 0.0}

输入: This is an English sentence.
预测语种: Latin, 置信度: 0.6048
所有分数: {'Latin': 0.6048129797024254, 'Traditional_Chinese': 0.0, 'Japanese_Hiragana': 0.0, 'Simplified_Chinese': 0.0, 'Korean_Hangul': 0.0, 'Cyrillic': 0.0, 'Thai': 0.0, 'Japanese_Katakana': 0.0}

输入: これは日本語の文です。
预测语种: Japanese_Hiragana, 置信度: 0.3434
所有分数: {'Latin': 0.0, 'Traditional_Chinese': 0.01056772297719242, 'Japanese_Hiragana': 0.3434195411527941, 'Simplified_Chinese': 0.0, 'Korean_Hangul': 0.0, 'Cyrillic': 0.0, 'Thai': 0.0, 'Japanese_Katakana': 0.0}

输入: 안녕하세요 저는 한국 사람입니다.
预测语种: Korean_Hangul, 置信度: 0.3301
所有分数: {'Latin': 0.0, 'Traditional_Chinese': 0.0, 'Japanese_Hiragana': 0.0, 'Simplified_Chinese': 0.0, 'Korean_Hangul': 0.33008563064981494, 'Cyrillic': 0.0, 'Thai': 0.0, 'Japanese_Katakana': 0.0}

输入: 你好，我是一个中国人123542ABCDEWRSSSABCDEWRSSSABCDEWRSSSABCDEWRSSSABCDEWRSSSABCDEWRSSS3123123123。
预测语种: Latin, 置信度: 0.0329
所有分数: {'Latin': 0.03294101403288453, 'Traditional_Chinese': 0.0, 'Japanese_Hiragana': 0.0, 'Simplified_Chinese': 0.0012485128992744006, 'Korean_Hangul': 0.0, 'Cyrillic': 0.0, 'Thai': 0.0, 'Japanese_Katakana': 0.0}

```

#### Datos de prueba:
Durante el desarrollo y las pruebas, utilice todos los archivos de texto en `tests/fixtures` para realizar pruebas, o emplee más muestras de datos. A continuación se proporcionan los enlaces de almacenamiento en la nube para las muestras de datos:

20230101.zip Archivado: 7.34 GB, Original: 17.11 GB
[百度网盘](https://pan.baidu.com/s/1TLEkczf5_pQlWcXwLPPcEw?pwd=78uq)

1_dir_need_check.zip Archivado: 9.94 GB, Original: 22.98 GB
[百度网盘](https://pan.baidu.com/s/1IitNwAIbeZH9-Ah5eGCHfA?pwd=49yc)

20221224.zip Archivado: 4.57 GB, Original: 13.45 GB
[百度网盘](https://pan.baidu.com/s/19DWSU68IukKWQqoEgjuVRQ?pwd=dh2n)

20221225.zip Archivado: 7.53 GB, Original: 17.68 GB
[百度网盘](https://pan.baidu.com/s/1nTVNwayGfon8-R87TuCYfQ?pwd=76jy)


#### Ejemplos de uso de conversión de codificación:
AVISO: Por defecto, los archivos se convierten al formato utf-8. Antes y después de la conversión, el archivo original se copia in situ con formato raw para realizar una copia de seguridad, y se sobrescribe con el formato utf-8. El flujo de operación es el siguiente:

1: Copiar `test.txt` in situ a `test.raw`

2: Sobrescribir `test.txt` con el formato utf-8

```
usage: convert_files.py [-h] [-p PROCESS_NUM] [-m MODE] -i inputDirectory [-step PROCESS_STEP] [-r check_result_file_name]
                        [-o convert_result_file_name] [-u]

Realizar una detección rápida de codificaciones en una gran cantidad de archivos de texto para facilitar la limpieza de datos del proyecto de corpus mnbvc.

Argumentos opcionales:
  -h, --help            mostrar este mensaje de ayuda y salir
  -p PROCESS_NUM, --process_num PROCESS_NUM
                        Especificar el número de procesos, por defecto 4
  -m MODE, --mode MODE  mode=1 mnbvc, mode=2 ccharde (por defecto)
  -i inputDirectory     inputDirectory es el directorio que necesita ser detectado
  -step PROCESS_STEP    Paso de ejecución, 1 para detección de codificación, 2 para conversión de codificación, 3 para verificación automática, por defecto 1
  -r check_result_file_name
                        Especificar el nombre del archivo de resultados de detección de codificación
  -o convert_result_file_name
                        Especificar el nombre del archivo de resultados de conversión de codificación
  -u                    Restaurar archivos
```
Ejemplo de detección de codificación:
`python convert_files.py -i /Users/alan/temp_test -step 1 -r check_result.csv`

```
###################################### Inicio del Paso 1 ######################################
Progreso de detección de codificación: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2152/2152 [00:00<00:00, 3275.19it/s]
Los resultados de la detección se han guardado en el archivo check_result.csv, ¡por favor revise!
###################################### Fin del Paso 1 ######################################
```

Ejemplo de conversión de codificación (después de la conversión, se añade automáticamente el paso 3 para verificar si los archivos convertidos a utf-8 son correctos):
`python convert_files.py -i /Users/alan/temp_test/gbk_test -step 2 -r check_result.csv -o convert_result.csv`
```
###################################### Inicio del Paso 2 ######################################
Progreso de conversión de codificación: 100%|████████████████████████████████████████████████████████████████████████████████████████| 9/9 [00:00<00:00, 105.52it/s]
Número total de archivos: 9
Archivos convertidos correctamente: 8
Archivos con error en la conversión: 1
/Users/alan/temp_test/gbk_test/1184.txt error al convertir de gb18030 a utf8, 'gb18030' codec can't decode bytes in position 54623-54623: There are invalid bytes in the string "肆郊嵌狻\xa3
   "
La lista de archivos con error en la conversión se ha guardado en: convert_result.csv
###################################### Fin del Paso 2 ######################################
###################################### Inicio del Paso 3 ######################################
Inicio de verificación secundaria de archivos
Directorio de detección: /Users/alan/temp_test/gbk_test
Progreso de verificación: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 8/8 [00:00<00:00, 4145.08it/s]
Fin de la verificación secundaria de archivos
¡Se ha completado la verificación de todos los archivos txt convertidos a utf-8!
###################################### Fin del Paso 3 ######################################
......
```

Realizar únicamente la verificación secundaria de archivos utf-8:
`python convert_files.py -i /Users/alan/temp_test -step 3 -r check_result.csv`

```
###################################### Inicio del Paso 3 ######################################
Inicio de verificación secundaria de archivos
Directorio de detección: /Users/alan/temp_test
Progreso de verificación: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2134/2134 [00:00<00:00, 8758.18it/s]
Fin de la verificación secundaria de archivos
¡Se ha completado la verificación de todos los archivos txt convertidos a utf-8!
###################################### Fin del Paso 3 ######################################
```

#### Ejemplo de uso de pre_check.py
```
usage: convert_files.py [-h] [-p PROCESS_NUM] [-m MODE] -i inputDirectory [-r check_result_file_name]
convert_files.py: error: los siguientes argumentos son requeridos: -i

python pre_check.py -i /Users/alan/temp_test/20230101/aliyun.20230101.8.武侠小说
Progreso de detección 1: 100%|███████████████████████████████████████████████████████████████| 3724/3724 [00:01<00:00, 3153.64its]
Progreso de detección 2: 100%|███████████████████████████████████████████████████████████████| 3724/3724 [00:00<00:00, 4288.96its]
Los resultados de error de la detección se han guardado en el archivo check_result_1706672423.csv, ¡por favor revise!
```

#### Ejemplos de prueba de detección de codificación mixta chino-inglés
```
usage: python examples/check_zh_en.py
tests/fixtures/test_sample_gbk_锟斤铐.txt False zh,en percentage:82.76%
tests/fixtures/test_sample_euc-jp.txt False zh,en percentage:73.31%
tests/fixtures/test4.txt False zh,en percentage:0.00%
tests/fixtures/test5.txt False zh,en percentage:83.59%
tests/fixtures/1045.txt True zh,en percentage:98.47%
tests/fixtures/test_sample_gbk_with_cp936_1.txt True zh,en percentage:99.31%
tests/fixtures/10.txt True zh,en percentage:98.79%
tests/fixtures/test2.txt False zh,en percentage:40.00%
tests/fixtures/test3.txt True zh,en percentage:100.00%
tests/fixtures/test.txt True zh,en percentage:100.00%
tests/fixtures/test_sample_big5.txt True zh,en percentage:100.00%
tests/fixtures/18.txt False zh,en percentage:96.84%
```

#### Enlace del wiki:
https://wiki.mnbvc.org/doku.php/ylzq

#### Enlace de la herramienta GUI:
Para facilitar el desarrollo de detección y conversión de codificaciones.
https://github.com/alanshi/mnbvc-charset-tool
