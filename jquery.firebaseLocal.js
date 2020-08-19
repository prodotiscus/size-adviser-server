var firebaseLocal = {
    sessionID: templateSessionID,
    setSessionData: function (sessionID, userEmail, userName, success, failure) {
        $.get(
            "/firebase/set_session_data",
            {
                session_id: sessionID,
                user_email: userEmail,
                user_name: userName
            }
        ).success(success).fail(failure);
    }
};