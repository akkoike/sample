import java.sql.*;

class SampleSelect {
    public static void main(String[] args) {
        Connection myDbConn;
        try {
            String url ="jdbc:mysql://metatestmysql.mysql.database.azure.com:3306/instancemeta?useSSL=true&requireSSL=false";
            String user = "azure01@metatestmysql";
            String pass = "Passw@rd";
            myDbConn = DriverManager.getConnection(url, user, pass);
                try {
                    String sqlquery = "select * from instancemetadata where timestamp like '2018-05-07%'";
                    PreparedStatement pstmt = myDbConn.prepareStatement(sqlquery);
                    ResultSet rs = pstmt.executeQuery();
                    while(rs.next()){
                        System.out.print(rs.getString("id") + ",");
                        System.out.print(rs.getString("timestamp") + ",");
                        System.out.print(rs.getString("targetnode") + ",");
                        System.out.print(rs.getString("documentincarnation") + ",");
                        System.out.print(rs.getString("eventid") + ",");
                        System.out.print(rs.getString("eventstatus") + ",");
                        System.out.print(rs.getString("eventtype") + ",");
                        System.out.print(rs.getString("resourcetype") + ",");
                        System.out.print(rs.getString("resources") + ",");
                        System.out.println(rs.getString("notbefore"));
                    }
                        pstmt.close();
                        rs.close();
                } finally {
                    myDbConn.close();
                }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}