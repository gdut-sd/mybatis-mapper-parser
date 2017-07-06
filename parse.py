# -*- coding: utf-8 -*-

import re
import sys


# 用于拼接字符串，并添加换行
def append_line(s, attachment=''):
    return s + attachment + '\n'  # 返回拼接后的字符串


# 驼峰命名到下划线命名的转换
def convert_camel_to_under_score(s):
    r = ""
    for c in s:
        if re.match(r'[A-Z]', c):
            r += '_'
            r += c.lower()
        else:
            r += c
    return r


def load_file():
    file_name = sys.argv[1]
    table_name = sys.argv[2]
    entity_name_begin = 0
    base_dir = ''
    if file_name.__contains__("\\") > 0:  # 是绝对路径，则需要解析出文件所在的目录
        entity_name_begin = file_name.rindex("\\") + 1
        base_dir = file_name[:entity_name_begin]
    entity_name = file_name[entity_name_begin:file_name.rindex('.java')]

    f = open(file_name, 'rb')
    content = f.read().decode("utf8")

    return entity_name, table_name, content, base_dir


def parse_content(entity_name, table_name, content):
    lines = content.splitlines()
    field_camel_name_list = []
    field_name_map = {}
    field_type_map = {}

    result = ''

    for line in lines:
        if line.startswith("package"):
            result = append_line(result, gen_package_and_import(line, entity_name))
            result = append_line(result, gen_basic_information(entity_name))
        elif line.strip().startswith('private') and not line.strip().startswith('private static'):
            # 抽取属性，生成属性名表
            field_type = line[line.index('private') + 8:line.rindex(' ')]
            field_name = line[line.index(field_type) + len(field_type) + 1: line.rindex(';')]
            field_camel_name_list.append(field_name)
            field_name_map[field_name] = convert_camel_to_under_score(field_name)
            field_type_map[field_name] = field_type
        elif line.strip().startswith('protected') and not line.strip().startswith('private static'):
            # 抽取属性，生成属性名表
            field_type = line[line.index('protected') + 10:line.rindex(' ')]
            field_name = line[line.index(field_type) + len(field_type) + 1: line.rindex(';')]
            field_camel_name_list.append(field_name)
            field_name_map[field_name] = convert_camel_to_under_score(field_name)
            field_type_map[field_name] = field_type

    result = append_line(result, gen_insert_method(entity_name, table_name, field_camel_name_list, field_name_map,
                                                   field_type_map))
    result = append_line(result, gen_select_method(entity_name, table_name, field_camel_name_list, field_name_map,
                                                   field_type_map))
    result = append_line(result, gen_update_method(entity_name, table_name, field_camel_name_list, field_name_map,
                                                   field_type_map))
    result = append_line(result, gen_delete_method(entity_name, table_name, field_camel_name_list, field_name_map,
                                                   field_type_map))
    result = append_line(result, '}')

    return result


def gen_package_and_import(package_line, entity_name):
    result = ''

    # 解析出entity所在的package，生成Mapper所在的package
    entity_package = package_line
    # Mapper所在的package与entity所在的package同级
    mapper_package = entity_package[:entity_package.rindex(".")] + ".mapper;"
    result = append_line(result, mapper_package)

    entity_import = 'import ' + (entity_package[:-1] + '.' + entity_name + ';')[8:]
    mybatis_import = 'import org.apache.ibatis.annotations.*;'
    java_list_import = 'import java.util.List;'
    result = append_line(result)
    result = append_line(result, entity_import)
    result = append_line(result, mybatis_import)
    result = append_line(result, java_list_import)
    result = append_line(result)

    return result


def gen_basic_information(entity_name):
    mapper_annotation = "@Mapper"
    interface_definition = "public interface %sMapper {" % entity_name
    return mapper_annotation + '\n' + interface_definition + '\n'


def gen_insert_method(entity_name, table_name, field_camel_name_list, field_name_map, field_type_map):
    result = ""
    result = append_line(result, '    @Insert("INSERT INTO %s " +' % table_name)
    entity_name_lower_case = entity_name[:1].lower() + entity_name[1:]
    fs = ""
    cl = ""
    for e in field_camel_name_list:
        fs += ', ' + field_name_map[e]
        cl += ', #{%s.%s}' % (entity_name_lower_case, e)
    fs = fs[2:]
    cl = cl[2:]
    result = append_line(result, '            "( %s ) " +' % fs)
    result = append_line(result, '            "VALUES " +')
    result = append_line(result, '            "( %s )")' % cl)
    result = append_line(result, '    void insert(@Param("%s") %s %s);' % (
        entity_name_lower_case, entity_name, entity_name_lower_case))
    return result


def gen_select_method(entity_name, table_name, field_camel_name_list, field_name_map, field_type_map):
    result = ''
    pk = field_camel_name_list[0]
    result = append_line(result, '    @Select("SELECT * FROM %s " +' % table_name)
    result = append_line(result, '            "WHERE %s = #{%s}")' % (field_name_map[pk], pk))
    result = append_line(result, '    @Results({')
    rss = ""
    for e in field_camel_name_list:
        if e == pk:
            rss += '            @Result(property = "%s", column = "%s", id = true),\n' % (pk, field_name_map[pk])
        else:
            rss += '            @Result(property = "%s", column = "%s"),\n' % (e, field_name_map[e])
    rss = rss[:-2]
    result = append_line(result, rss)
    result = append_line(result, '    })')
    result = append_line(result, '    %s queryById(@Param("%s") %s %s);' % (entity_name, pk, field_type_map[pk], pk))
    return result


def gen_update_method(entity_name, table_name, field_camel_name_list, field_name_map, field_type_map):
    result = ''
    entity_name_lower_case = entity_name[:1].lower() + entity_name[1:]
    pk = field_camel_name_list[0]
    result = append_line(result, '    @Update("UPDATE %s SET " +' % table_name)
    uf = ""
    for e in field_camel_name_list:
        if e != pk:
            uf += '            "%s = #{%s.%s}, " +\n' % (field_name_map[e], entity_name_lower_case, e)
    uf = uf[:-6] + ' " +'
    result = append_line(result, uf)
    result = append_line(result,
                         '            "WHERE %s = #{%s.%s}")' % (pk, entity_name_lower_case, field_name_map[pk]))
    result = append_line(result, '    void update(@Param("%s") %s %s);' % (
        entity_name_lower_case, entity_name, entity_name_lower_case))
    return result


def gen_delete_method(entity_name, table_name, field_camel_name_list, field_name_map, field_type_map):
    result = ''
    pk = field_camel_name_list[0]
    result = append_line(result,
                         '    @Delete("DELETE FROM %s WHERE %s = #{%s}")' % (table_name, field_name_map[pk], pk))
    result = append_line(result, '    void delete(@Param("%s") %s %s);' % (pk, field_type_map[pk], pk))
    return result


def output(entity_name, result_content, base_dir=''):
    output_file_name = "%s%sMapper.java" % (base_dir, entity_name)
    fo = open(output_file_name, "w")
    fo.write(result_content)


if __name__ == '__main__':
    en, tn, content, bdir = load_file()
    r = ''
    r = parse_content(en, tn, content)
    print r
    output(en, r, bdir)
