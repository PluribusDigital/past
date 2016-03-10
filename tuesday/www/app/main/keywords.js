app.controller('KeywordController', function ($scope, $http, $location, $routeParams) {
    /************************************************************************************************
     * Properties
     */
    $scope.doc_id = $routeParams.doc_id;
    $scope.corpus_id = $routeParams.corpus_id;

    $scope.fields = ['token', 'lemma', 'stem'];
    $scope.limits = [10, 20, 25, 50, 100];

    $scope.corpus = '';
    $scope.document = '';
    $scope.keywords = []

    /************************************************************************************************
    * Data Model Methods
    */

    $scope.onCorpusLoaded = function (data) {
        if (data != null) {
            $scope.corpus = data.name;
        }
    }

    $scope.onDocumentLoaded = function (data) {
        if (data != null) {
            $scope.document = data.title;
        }
    }

    $scope.onKeywordsLoaded = function (data) {
        $scope.keywords = data;
        if ($scope.keywords == null) {
            $scope.keywords = [];
            return;
        }
    }

    /************************************************************************************************
     * Actions
     */

    $scope.refresh = function () {
        var params = {};
        if ($scope.field != 'lemma')
            params.field = $scope.field;
        if ($scope.limit != 10)
            params.limit = $scope.limit;
        if ($scope.includeMorph)
            params.morph = 1;
        if ($scope.includePos)
            params.partOfSpeech = 1;
        if ($scope.includeSyntax)
            params.syntax = 1;

        var url = $location.path();
        var query = $.param(params);
        if (query !== '') {
            url = url + '?' + query;
        }

        $location.url(url);
    };

    /************************************************************************************************
     * Methods
     */

    $scope.buildBaseUrl = function () {
        url = 'http://' + $location.host() + ':' + $location.port();
        return url;
    };

    $scope.buildBaseApiUrl = function () {
        url = 'http://' + $location.host() + ':' + $location.port() + '/api/v1';
        return url;
    };

    $scope.initOptions = function () {
        var query = $location.search();

        $scope.includeMorph = ('morph' in query);
        $scope.includePos = ('partOfSpeech' in query);
        $scope.includeSyntax = ('syntax' in query);
        $scope.limit = ('limit' in query) ? parseInt(query['limit']) : 10;
        $scope.field = ('field' in query) ? query['field'] : 'lemma';
    };

    $scope.request = function (url, callback) {
        $http.get(url).then(
            function (response) { callback(response.data) },
            function (response) { alert(response.status) }
            );
    };

    /************************************************************************************************
     * Initialization
     */

    $scope.initOptions();
    $scope.apiBaseUrl = $scope.buildBaseApiUrl();
    $scope.baseUrl = $scope.buildBaseUrl();

    $scope.request($scope.apiBaseUrl + $location.url(), $scope.onKeywordsLoaded);

    if ($scope.corpus_id != undefined)
        $scope.request($scope.apiBaseUrl + '/corpus/' + $scope.corpus_id, $scope.onCorpusLoaded);
    if ($scope.doc_id != undefined)
        $scope.request($scope.apiBaseUrl + '/document/' + $scope.doc_id, $scope.onDocumentLoaded);

});