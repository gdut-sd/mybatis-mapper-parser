##简介
    这是一个利用Java实体类代码生成mybatis mapper接口的脚本

##背景
    平时写服务端代码，实体类属性名一般都是驼峰，而数据库表字段一般都是下划线的。
    当使用mybatis的时候，需要在Mapper接口上写SQL，以及数据库字段名和实体类属性名的映射，当字段多的是时候，写起来的就很繁琐，而且一不小心写错了，单元测试就跑不过了。
    所以就有了这个脚本。这个脚本的思路也很简单，就是文本解析，然后生成对应的Mapper接口代码。

##使用说明

###命令格式
* 使用python命令运行脚本，需要添加2个命令行参数：
  * fileName：文件名，可以是相对路径或绝对路径。
  * tableName：对应数据库的表名。
```
~: python parse.py fileName tableName
```

###特性
* 生成的文件会与目标文件位于同一个目录
* Mapper接口的package与实体类所在package同级，如实体类所在package为`com.sd.entity`，则生成的Mapper接口的package为`com.sd.mapper`
* 生成4个简单的CRUD方法
* SQL语句中，关键字全大写

###限制
1. 由于没有做错误处理，如果命令行参数数量不够，或者没有那个文件，脚本就会运行失败
2. 一个.java文件只能有一个类的定义（有非public类也不行）
3. .java文件格式需要经过format， 使用IntelliJ的默认代码格式，其他格式未作任何测试，不保证生成代码的效果
4. .java文件中，类的第一个非static属性作为主键
5. 类的static属性会被忽略

##实例

###源文件
```java
package com.sd.entity;

import java.util.Objects;

/**
 * @author SD
 */
public class User {

    private Integer userId;
    private String userName;
    private String password;

    private int state;

    private Role role;

    public User() {
    }

    public User(String userName, String password) {
        this.userName = userName;
        this.password = password;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public String getUserName() {
        return userName;
    }

    public String getPassword() {
        return password;
    }


    public void setUserName(String userName) {
        this.userName = userName;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public int getState() {
        return state;
    }

    public void setState(int state) {
        this.state = state;
    }

    public Role getRole() {
        return role;
    }

    public void setRole(Role role) {
        this.role = role;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return Objects.equals(userId, user.userId) &&
                Objects.equals(userName, user.userName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(userId, userName);
    }

    @Override
    public String toString() {
        return "User{" +
                "userId=" + userId +
                ", userName='" + userName + '\'' +
                ", password='" + password + '\'' +
                ", role=" + role +
                '}';
    }
}
```

###生成文件
```java
package com.sd.mapper;

import com.sd.entity.User;
import org.apache.ibatis.annotations.*;
import java.util.List;


@Mapper
public interface UserMapper {

    @Insert("INSERT INTO user " +
            "( user_id, user_name, password, state, role ) " +
            "VALUES " +
            "( #{user.userId}, #{user.userName}, #{user.password}, #{user.state}, #{user.role} )")
    void insert(@Param("user") User user);

    @Select("SELECT * FROM user " +
            "WHERE user_id = #{userId}")
    @Results({
            @Result(property = "userId", column = "user_id", id = true),
            @Result(property = "userName", column = "user_name"),
            @Result(property = "password", column = "password"),
            @Result(property = "state", column = "state"),
            @Result(property = "role", column = "role")
    })
    User queryById(@Param("userId") Integer userId);

    @Update("UPDATE user SET " +
            "user_name = #{user.userName}, " +
            "password = #{user.password}, " +
            "state = #{user.state}, " +
            "role = #{user.role} " +
            "WHERE userId = #{user.user_id}")
    void update(@Param("user") User user);

    @Delete("DELETE FROM user WHERE user_id = #{userId}")
    void delete(@Param("userId") Integer userId);

}

```